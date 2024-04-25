import luadata
import sys

output_file = "TalentData.lua"
project_id = ""

class TalentData:
	index: int
	talentID: int
	name: str
	icon: int

class SpecData:
	specID: int
	specIndex: int
	specName: str
	specIcon: int
	className: str
	classFileName: str
	lastUpdateBuild: str
	talents: list[TalentData]

	def talents_to_string(self):
		result: str = ""
		result += "\t-- " + self.specName + " " + self.className + "\n"
		result += "\t[" + str(self.specID) + "] = {\n"

		result += self.talent_tab_to_string()

		result += "\t},\n"

		return result

	def talent_tab_to_string(self):
		result: str = ""

		for talent in self.talents:
			result += "\t\t\t{ id = " + str(talent.talentID) + ", name = \"" + str(talent.name) + "\", icon = " + str(talent.icon) + " },\n"

		return result


def parse_args():
	global output_file
	global project_id

	for i in range(1, len(sys.argv)):
		current = sys.argv[i]

		if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
			next = sys.argv[i + 1]

		if current == "--output":
			output_file = next
		elif current == "--project-id":
			project_id = next

def parse_spec_data(lua):
	data = SpecData()
	data.specID = lua["specID"]
	data.specIndex = lua["specIndex"]
	data.specName = lua["specName"]
	data.specIcon = lua["specIcon"]
	data.lastUpdateBuild = lua["lastUpdateBuild"]
	data.className = lua["className"]
	data.classFileName = lua["classFileName"]
	data.talents = parse_talent_table(lua["talents"])

	return data

def parse_talent_table(lua):
	result: list[TalentData] = []

	for talent in lua:
		data = TalentData()
		data.index = len(result)
		data.talentID = talent["talentID"]
		data.name = talent["name"]
		data.icon = talent["icon"]

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
	result += "--- @type LibTalentInfoClassic-1.0\n"
	result += "local LibTalentInfoClassic = LibStub and LibStub(\"LibTalentInfoClassic-1.0\", true)\n"
	result += "local version = " + build + "\n\n"
	result += "if WOW_PROJECT_ID ~= " + project_id + " or LibTalentInfoClassic == nil or version <= LibTalentInfoClassic:GetTalentProviderVersion() then\n"
	result += "\treturn\n"
	result += "end\n\n"

	result += "--- @type table<integer,{[integer]: { id: integer, name: string, icon: integer }}>\n"
	result += "local specializations = {\n"

	classes = generate_spec_list(specs)

	for k, v in classes.items():
		result += "\t" + k + " = {\n"

		for s in v:
			if s is None:
				continue

			result += "\t\t[" + str(s.specIndex) + "] = { id = " + str(s.specID) + ", name = \"" + s.specName + "\", icon = " + str(s.specIcon) + " }, -- " + s.specName + "\n"

		result += "\t},\n"

	result += "}\n\n"

	result += "--- @type table<integer,{ id: integer, name: string, icon: integer }>\n"
	result += "local talents = {\n"

	for spec in specs:
		result += spec.talents_to_string()

	result += "}\n\n"

	result += "LibTalentInfoClassic:RegisterTalentProvider({\n"
	result += "\tversion = version,\n"
	result += "\tspecializations = specializations,\n"
	result += "\ttalents = talents,\n"
	result += "})\n"

	return result

def get_build(data: SpecData):
	return data.lastUpdateBuild

parse_args()

lua = luadata.read("TalentExtractor.lua", encoding="utf-8")
specs: list[SpecData] = []

for spec in lua:
	specs.append(parse_spec_data(lua[spec]))

specs.sort(key=get_build, reverse=True)
build = specs[0].lastUpdateBuild

output = generate_lua_table(build, specs)

try:
	fs = open(output_file, "w", encoding="utf8")
	fs.write(output)
	fs.close
except Exception as fserr:
	print("failed to write file \"" + output_file + "\": " + str(fserr))
	exit(1)
