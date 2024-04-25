import luadata
import sys

output_file = "TalentData.lua"
project_id = ""

class TalentData:
	index: int
	talentID: int
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
				if j.talentID == i:
					if result:
						result += ", "

					result += str(j.talentID)


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

def parse_class_data(lua):
	data = ClassData()
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

		result.append(data)

	return result

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
	result += "if WOW_PROJECT_ID ~= " + project_id + " or LibTalentInfoClassic == nil or version <= LibTalentInfoClassic:GetTalentProviderVersion() then\n"
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
	return data.lastUpdateBuild

parse_args()

lua = luadata.read("TalentExtractor.lua", encoding="utf-8")
classes: list[ClassData] = []

for clazz in lua:
	classes.append(parse_class_data(lua[clazz]))

classes.sort(key=get_build, reverse=True)
build = classes[0].lastUpdateBuild

output = generate_lua_table(build, classes)

try:
	fs = open(output_file, "w", encoding="utf8")
	fs.write(output)
	fs.close
except Exception as fserr:
	print("failed to write file \"" + output_file + "\": " + str(fserr))
	exit(1)
