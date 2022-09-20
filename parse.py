from luaparser import ast
from luaparser import astnodes

class TalentData:
	index: int
	talentId: int
	name: str

class SpecData:
	specId: int
	specIndex: int
	specName: str
	className: str
	classFileName: str
	build: str
	talents: list[TalentData]
	pvpTalents: list[list[TalentData]]

	def talents_to_string(self):
		result: str = ""
		result += "\t-- " + self.specName + " " + self.className + "\n"
		result += "\t[" + str(self.specId) + "] = {\n"

		for i in range(len(self.talents)):
			result += "\t\t" + self.talent_row_to_string(i) + "\n"

		result += "\t},\n"

		return result

	def talent_row_to_string(self, index):
		result: str = ""
		result += str(self.talents[index].talentId) + ", "
		result += "-- "
		result += "[" + str(index) + "] "
		result += str(self.talents[index].name)
		result += ", "

		return result

	def pvp_talents_to_string(self):
		result: str = ""
		result += "\t-- " + self.specName + " " + self.className + "\n"
		result += "\t[" + str(self.specId) + "] = {\n"

		for i in range(len(self.pvpTalents)):
			result += "\t\t[" + str(i + 1) +"] = " + self.pvp_talent_row_to_string(self.pvpTalents[i]) + "\n"

		result += "\t},\n"

		return result

	def pvp_talent_row_to_string(self, row: list[TalentData]):
		result: str = ""
		result += "{ "

		if len(row) > 0:
			for talent in row:
				result += str(talent.talentId) + ", "

			result += "}, -- "

			for i in range(len(row)):
				result += str(row[i].name)

				if i < len(row) - 1:
					result += ", "
		else:
			result += "},"

		return result

def parse_spec_data(fields: list[ast.Field]):
	data = SpecData()

	for field in fields:
		key = field.key.s

		if key == "specID":
			data.specId = field.value.n
		if key == "specIndex":
			data.specIndex = field.value.n
		if key == "lastUpdateBuild":
			data.build = field.value.s
		elif key == "specName":
			data.specName = field.value.s
		elif key == "className":
			data.className = field.value.s
		elif key == "classFileName":
			data.classFileName = field.value.s
		elif key == "talents":
			data.talents = parse_talent_table(field.value.fields)
		elif key == "pvpTalents":
		 	data.pvpTalents = parse_pvp_talent_table(field.value.fields)

	return data

def parse_pvp_talent_table(fields: list[astnodes.Field]):
	result: list[list[TalentData]] = []

	for field in fields:
		index = field.key.n - 1

		try:
			result[index] = parse_pvp_talents(field.value.fields)
		except IndexError:
			for _ in range(index - len(result) + 1):
				result.append(None)
			result[index] = parse_pvp_talents(field.value.fields)

	return result

def parse_talent_table(trees: list[astnodes.Field]):
	result: list[TalentData] = []

	for tree in trees:
		parse_talent_node(tree.value.fields, result)

	return result

def parse_talent_node(fields: list[astnodes.Field], result: list[TalentData]):
	for field in fields:
		key = field.key.s

		if key == "entryIDs":
			parse_talent_node_entries(field.value.fields, result)

def parse_talent_node_entries(entries: list[astnodes.Field], result: list[TalentData]):
	for entry in entries:
		data = TalentData()
		parse_talent_node_entry(entry.value.fields, data)
		result.append(data)

def parse_talent_node_entry(fields: list[astnodes.Field], data: TalentData):
	for field in fields:
		key = field.key.s

		if key == "spellID":
			data.talentId = field.value.n
		elif key == "name":
			data.name = field.value.s

def parse_pvp_talents(fields: list[astnodes.Field]):
	result: list[TalentData] = []

	for field in fields:
		data = TalentData()
		data.index = field.key.n - 1
		parse_pvp_talent(field.value.fields, data)

		try:
			result[data.index] = data
		except IndexError:
			for _ in range(data.index - len(result) + 1):
				result.append(None)
			result[data.index] = data

	return result

def parse_pvp_talent(fields: list[astnodes.Field], data: TalentData):
	for field in fields:
		key = field.key.s

		if key == "talentID":
			data.talentId = field.value.n
		elif key == "name":
			data.name = field.value.s

def generate_spec_list(specs: list[SpecData]):
	result: dict[str,list[SpecData]] = {}

	for spec in specs:
		if spec is None:
			continue

		if not spec.classFileName in result:
			result[spec.classFileName] = []

		data = result[spec.classFileName]

		try:
			data[spec.specIndex] = spec
		except IndexError:
			for _ in range(spec.specIndex - len(data) + 1):
				data.append(None)
			data[spec.specIndex] = spec

	return result

def generate_lua_table(build: str, specs: list[SpecData]):
	result: str = ""
	result += "local LibTalentInfo = LibStub and LibStub(\"LibTalentInfo-1.0\", true)\n"
	result += "local version = " + build + "\n\n"
	result += "if WOW_PROJECT_ID ~= WOW_PROJECT_MAINLINE or LibTalentInfo == nil or version <= LibTalentInfo:GetTalentProviderVersion() then\n"
	result += "\treturn\n"
	result += "end\n\n"

	result += "--- @type table<string,table<integer,integer>>\n"
	result += "local specializations = {\n"

	classes = generate_spec_list(specs)

	for k, v in classes.items():
		result += "\t" + k + " = {\n"

		for s in v:
			if s is None:
				continue

			result += "\t\t[" + str(s.specIndex) + "] = " + str(s.specId) + ", -- " + s.specName + "\n"

		result += "\t},\n"

	result += "}\n\n"
	result += "--- @type table<integer,integer[]>\n"
	result += "local talents = {\n"

	for spec in specs:
		result += spec.talents_to_string()

	result += "}\n\n"
	result += "--- @type table<integer,table<integer,integer[]>>\n"
	result += "local pvpTalents = {\n"

	for spec in specs:
		result += spec.pvp_talents_to_string()

	result += "}\n\n"
	result += ""
	result += "LibTalentInfo:RegisterTalentProvider({\n"
	result += "\tversion = version,\n"
	result += "\tspecializations = specializations,\n"
	result += "\ttalents = talents,\n"
	result += "\tpvpTalentSlotCount = 3,\n"
	result += "\tpvpTalents = pvpTalents\n"
	result += "})\n"

	return result

def get_build(data: SpecData):
	return data.build

def get_spec_id(data: SpecData):
	return data.specId

try:
	fs = open("TalentExtractor.lua", "r", encoding="utf8")
	src = fs.read()
	fs.close
except Exception as fserr:
	print("failed to read file \"TalentExtractor.lua\": " + str(fserr))
	exit(1)

tree = ast.parse(src)
specs: list[SpecData] = []

for field in tree.body.body[0].values[0].fields:
	specs.append(parse_spec_data(field.value.fields))

specs.sort(key=get_build, reverse=True)
build = specs[0].build

specs.sort(key=get_spec_id)
output = generate_lua_table(build, specs)

try:
	fs = open("TalentDataRetail.lua", "w", encoding="utf8")
	fs.write(output)
	fs.close
except Exception as fserr:
	print("failed to write file \"TalentDataRetail.lua\": " + str(fserr))
	exit(1)
