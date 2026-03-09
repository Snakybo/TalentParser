import luadata
import sys
import argparse

class Class:
	id: str
	name: str

class Specialization:
	index: int
	id: int
	name: str
	icon: int
	clazz: str

class Talent:
	index: int
	id: int
	name: str
	icon: int

class Cache:
	min_interface_version: int
	max_interface_version: int
	build_id: int
	keys: list[object]
	classes: list[Class]
	specializations: dict[str, list[Specialization]]
	talents: dict[object, list[Talent]]
	pvp_talents: dict[object, list[Talent]]

def get_class_id(data: Class):
	return data.id

def get_specialization_id(data: Specialization):
	return data.id

def get_talent_id(data: Talent):
	return data.id

def name_to_string(name: str):
	if name == "nil":
		return "nil"

	return f"\"{name}\""

def indent(count: int):
	return "\t" * count

def classes_to_string(indent_level: int, classes: list[Class]):
	result = "{\n"

	for current in classes:
		result += f"{indent(indent_level + 1)}{name_to_string(current.id)},\n"

	result += f"{indent(indent_level)}}}"
	return result

def specializations_to_string(indent_level: int, classes: list[Class], specializations: dict[str, list[Specialization]]):
	result = "{\n"

	for clazz in classes:
		result += f"{indent(indent_level + 1)}[{name_to_string(clazz.id)}] = {{\n"

		for specialization in specializations[clazz.id]:
			result += f"{indent(indent_level + 2)}[{specialization.index}] = {{ id = {specialization.id}, name = {name_to_string(specialization.name)}, icon = {specialization.icon} }},\n"

		result += f"{indent(indent_level + 1)}}},\n"

	result += f"{indent(indent_level)}}}"
	return result

def talents_to_string(indent_level: int, keys: list[object], talents: dict[object, list[Talent]]):
	result = "{\n"

	for key in keys:
		result += f"{indent(indent_level + 1)}[{name_to_string(key) if isinstance(key, str) else key }] = {{\n"

		for talent in talents[key]:
			result += f"{indent(indent_level + 2)}{{ id = {talent.id}, name = {name_to_string(talent.name)}, icon = {talent.icon} }},\n"

		result += f"{indent(indent_level + 1)}}},\n"

	result += f"{indent(indent_level)}}}"
	return result

def cache_to_string(cache: Cache):
	return f"""-- MIT License
--
-- Copyright (c) 2026 Kevin Krol
--
-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:
--
-- The above copyright notice and this permission notice shall be included in all
-- copies or substantial portions of the Software.
--
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-- SOFTWARE.

local LibTalentInfo = LibStub and LibStub(\"LibTalentInfo-1.0\", true)

local interfaceVersion = select(4, GetBuildInfo())

if LibTalentInfo == nil or interfaceVersion < {cache.min_interface_version} or interfaceVersion >= {cache.max_interface_version} then
	return
end

--- @type LibTalentInfo-1.0.Provider
LibTalentInfo:SetProvider({{
	build = {cache.build_id},
	classes = {classes_to_string(1, cache.classes)},
	specializations = {specializations_to_string(1, cache.classes, cache.specializations)},
	talents = {talents_to_string(1, cache.keys, cache.talents)},
	pvpTalents = {talents_to_string(1, cache.keys, cache.pvp_talents)}
}})
"""

def parse_lua_class(target: list[Class], lua):
	result = Class()
	result.id = lua["classFileName"]
	result.name = lua["className"]

	if not any(other.id == result.id for other in target):
		target.append(result)

	return result

def parse_lua_specialization(target: list[Specialization], lua):
	if "specIndex" in lua:
		result = Specialization()
		result.index = lua["specIndex"]
		result.id = lua["specId"]

		if "specName" in lua:
			result.name = lua["specName"]
			result.icon = lua["specIcon"]
		else:
			result.name = "nil"
			result.icon = "nil"

		target.append(result)

def parse_lua_talents(target: list[Talent], lua, key: str):
	if key in lua:
		for data in lua[key]:
			talent = Talent()
			talent.id = data["id"]
			talent.name = data["name"]
			talent.icon = data["icon"]
			target.append(talent)

def parse_lua(args):
	lua = luadata.read(args.input, encoding="utf-8")
	cache = Cache()
	cache.keys = []
	cache.classes = []
	cache.specializations = {}
	cache.talents = {}
	cache.pvp_talents = {}
	cache.min_interface_version = lua["minInterfaceVersion"]
	cache.max_interface_version = lua["maxInterfaceVersion"]
	cache.build_id = lua["lastUpdateBuild"]

	for key in lua["data"]:
		data = lua["data"][key]

		cache.keys.append(key)

		clazz = parse_lua_class(cache.classes, data)

		parse_lua_specialization(cache.specializations.setdefault(clazz.id, []), data)
		parse_lua_talents(cache.talents.setdefault(key, []), data, "talents")
		parse_lua_talents(cache.pvp_talents.setdefault(key, []), data, "pvpTalents")

	cache.keys.sort()
	cache.classes.sort(key=get_class_id)

	for clazz in cache.classes:
		cache.specializations[clazz.id].sort(key=get_specialization_id)

	for key in cache.keys:
		cache.talents[key].sort(key=get_talent_id)
		cache.pvp_talents[key].sort(key=get_talent_id)

	return cache_to_string(cache)

def write_output(args, result):
	try:
		fs = open(args.output, "w", encoding="utf8")
		fs.write(result)
		fs.close
	except Exception as fserr:
		print("failed to write file \"" + args.output + "\": " + str(fserr))
		exit(1)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("input", type=str, help="the input Lua file")
	parser.add_argument("-o", "--output", type=str, help="the output Lua file", default="TalentData.lua")

	args = parser.parse_args()
	result = parse_lua(args)
	write_output(args, result)
