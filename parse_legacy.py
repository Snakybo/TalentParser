from luaparser import ast
from luaparser import astnodes

class TalentData:
	index: int
	talentId: int
	name: str

class ClassData:
	className: str
	classFileName: str
	build: str
	talents: list[TalentData]

	def talents_to_string(self):
		result: str = ""
		result += "\t" + str(self.classFileName) + " = {\n"

		for i in range(3):
			if i > 0:
				result += ",\n"

			result += "\t\t[" + str(i + 1) + "] = { " + self.talent_tab_to_string(i) + " }"

		result += "\n\t},\n"

		return result

	def talent_tab_to_string(self, tab):
		result: str = ""

		startIndex: int = tab * 40 + 1
		endIndex: int = startIndex + 40

		for i in range(startIndex, endIndex):
			for j in self.talents:
				if j.talentId == i:
					if result:
						result += ", "

					result += str(j.talentId)


		return result

def parse_class_data(fields: list[ast.Field]):
	data = ClassData()

	for field in fields:
		key = field.key.s

		if key == "lastUpdateBuild":
			data.build = field.value.s
		elif key == "className":
			data.className = field.value.s
		elif key == "classFileName":
			data.classFileName = field.value.s
		elif key == "talents":
			data.talents = parse_talent_table(field.value.fields)

	return data

def parse_talent_table(fields: list[astnodes.Field]):
	result: list[TalentData] = []

	for field in fields:
		data = TalentData()
		data.index = field.key.n - 1
		parse_talent(field.value.fields, data)

		try:
			result[data.index] = data
		except IndexError:
			for _ in range(data.index - len(result) + 1):
				result.append(None)
			result[data.index] = data

	return result

def parse_talent(fields: list[astnodes.Field], data: TalentData):
	for field in fields:
		key = field.key.s

		if key == "talentID":
			data.talentId = field.value.n
		elif key == "name":
			data.name = field.value.s

def generate_class_list(classes: list[ClassData]):
	result: list[str] = []

	for clazz in classes:
		if clazz is None:
			continue

		result.append(clazz.classFileName)

	return result

def generate_lua_table(build: str, classes: list[ClassData]):
	result: str = ""
	result += "--- @type LibTalentInfoClassic\n"
	result += "local LibTalentInfoClassic = LibStub and LibStub(\"LibTalentInfoClassic-1.0\", true)\n"
	result += "local version = " + build + "\n\n"
	result += "if WOW_PROJECT_ID ~= WOW_PROJECT_BURNING_CRUSADE_CLASSIC or LE_EXPANSION_LEVEL_CURRENT ~= LE_EXPANSION_WRATH_OF_THE_LICH_KING or LibTalentInfoClassic == nil or version <= LibTalentInfoClassic:GetTalentProviderVersion() then\n"
	result += "\treturn\n"
	result += "end\n\n"

	result += "--- @type string[]\n"
	result += "local classes = {\n"

	class_list = generate_class_list(classes)

	for clazz in class_list:
		result += "\t\"" + clazz + "\",\n"

	result += "}\n\n"

	result += "--- @type table<integer,integer[]>\n"
	result += "local talents = {\n"

	for clazz in classes:
		result += clazz.talents_to_string()
		pass

	result += "}\n\n"

	result += "LibTalentInfoClassic:RegisterTalentProvider({\n"
	result += "\tversion = version,\n"
	result += "\tclasses = classes,\n"
	result += "\ttalents = talents,\n"
	result += "})\n"

	return result

def get_build(data: ClassData):
	return data.build

try:
	fs = open("TalentExtractor.lua", "r", encoding="utf8")
	src = fs.read()
	fs.close
except Exception as fserr:
	print("failed to read file \"TalentExtractor.lua\": " + str(fserr))
	exit(1)

tree = ast.parse(src)
classes: list[ClassData] = []

for field in tree.body.body[0].values[0].fields:
	classes.append(parse_class_data(field.value.fields))

classes.sort(key=get_build, reverse=True)
build = classes[0].build

output = generate_lua_table(build, classes)

try:
	fs = open("TalentDataWOTLK.lua", "w", encoding="utf8")
	fs.write(output)
	fs.close
except Exception as fserr:
	print("failed to write file \"TalentDataWOTLK.lua\": " + str(fserr))
	exit(1)
