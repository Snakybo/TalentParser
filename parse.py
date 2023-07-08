import luadata

class PvPTalentData:
	index: int
	talentID: int
	name: str

class SpecData:
	specId: int
	specIndex: int
	specName: str
	className: str
	classFileName: str
	lastUpdateBuild: str
	pvpTalents: list[PvPTalentData]

	def pvp_talents_to_string(self):
		result: str = ""
		result += "\t-- " + self.specName + " " + self.className + "\n"
		result += "\t[" + str(self.specID) + "] = "
		result += self.pvp_talent_row_to_string(self.pvpTalents)
		result += "\n"

		return result

	def pvp_talent_row_to_string(self, row: list[PvPTalentData]):
		result: str = ""
		result += "{ "

		if len(row) > 0:
			for talent in row:
				result += str(talent.talentID) + ", "

			result += "}, -- "

			for i in range(len(row)):
				result += str(row[i].name)

				if i < len(row) - 1:
					result += ", "
		else:
			result += "},"

		return result

def parse_spec_data(lua):
	data = SpecData()
	data.specID = lua["specID"]
	data.specIndex = lua["specIndex"]
	data.lastUpdateBuild = lua["lastUpdateBuild"]
	data.specName = lua["specName"]
	data.className = lua["className"]
	data.classFileName = lua["classFileName"]
	data.pvpTalents = parse_pvp_talents(lua["pvpTalents"])

	return data

def parse_pvp_talents(lua):
	result: list[PvPTalentData] = []

	for talent in lua:
		data = PvPTalentData()
		data.index = len(result)
		data.talentID = talent["talentID"]
		data.name = talent["name"]

		result.append(data)

	return result

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

			result += "\t\t[" + str(s.specIndex) + "] = " + str(s.specID) + ", -- " + s.specName + "\n"

		result += "\t},\n"

	result += "}\n\n"
	result += "--- @type table<integer,integer[]>\n"
	result += "local pvpTalents = {\n"

	for spec in specs:
		result += spec.pvp_talents_to_string()

	result += "}\n\n"
	result += ""
	result += "LibTalentInfo:RegisterTalentProvider({\n"
	result += "\tversion = version,\n"
	result += "\tspecializations = specializations,\n"
	result += "\tpvpTalents = pvpTalents\n"
	result += "})\n"

	return result

def get_build(data: SpecData):
	return data.lastUpdateBuild

def get_spec_id(data: SpecData):
	return data.specID

lua = luadata.read("TalentExtractor.lua", encoding="utf-8")
specs: list[SpecData] = []

for spec in lua:
	specs.append(parse_spec_data(lua[spec]))

specs.sort(key=get_build, reverse=True)
build = specs[0].lastUpdateBuild

specs.sort(key=get_spec_id)
output = generate_lua_table(build, specs)

try:
	fs = open("TalentDataRetail.lua", "w", encoding="utf8")
	fs.write(output)
	fs.close
except Exception as fserr:
	print("failed to write file \"TalentDataRetail.lua\": " + str(fserr))
	exit(1)
