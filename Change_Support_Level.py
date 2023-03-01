import os
import sys
import zlib
import argparse

Running_Path = os.path.dirname(os.path.realpath(__file__))

def Patch_CRC32(fileContent, Outfile):
	fileContent = fileContent[:-4]
	with open(Outfile, mode='wb') as file:
		file.write(fileContent+zlib.crc32(fileContent).to_bytes(4, 'little'))

def Get_Support_Paaring(Names):
	if ":" in Names:
		Name_list = {}
		Names = Names.split(":")
		with open(os.path.join(Running_Path,'English_Name_list.txt'), encoding='utf-8') as file:
			for Name_Pair in file.read().splitlines():
				Name_Pair_list = Name_Pair.split(":")
				Name_list[Name_Pair_list[0]] = Name_Pair_list[1]

		Names = Name_list[Names[0]], Name_list[Names[1]] 		
	else:
		Names = Names.split("|")

	if Names[0] == Names[1]:
		return False

	with open(os.path.join(Running_Path, 'Sorted_Support_Paarings.txt'), encoding='utf-8') as file:
		for Paaring in file.read().splitlines():
			if (Names[0] in Paaring) & (Names[1] in Paaring):
				return Paaring

	return False			

def Support_Options(Filepath, Outfile, Change_Support_Action, Support_level, Support_Dialoge_value, Paaring_Name):
	Support_Paarings = {}
	if Change_Support_Action == "1":
		Support_Paarings[Paaring_Name] = None
	else:
		with open(os.path.join(Running_Path, 'Sorted_Support_Paarings.txt'), encoding='utf-8') as file:
			for Paaring in file.read().splitlines():
				Support_Paarings[Paaring] = None

	with open(Filepath, mode='rb') as file:
		fileContent = bytearray(file.read())
		offset = 0
		while True:
			offset = fileContent.find(b'\x50\x00\x49\x00\x44\x00\x5f\x00', offset+8)
			if offset == -1:
				break
			Suffix = fileContent.find(b'\x01\x00\x00\x00', offset+8, offset+44)
			if Suffix != -1:
				if bytes(fileContent[offset:Suffix]).decode('utf-16', errors='ignore') in Support_Paarings:
					if Change_Support_Action == "2":
						fileContent[Suffix+4] = int(Support_level)

					if Support_Dialoge_value != "ND":
						if Support_Dialoge_value == "HD":
							fileContent[Suffix+5] = 124 + fileContent[Suffix+4]
						else:
							fileContent[Suffix+5] = int(Support_Dialoge_value)	

	Patch_CRC32(fileContent, Outfile)				

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Fire Emblem Engage Support Dialoge Patcher')
	parser.add_argument('-SA', '--Support_Action',
		action="store", dest="Change_Support_Action",
		help="Action for Support Patching 0: No changes 1: Use only offered Support Pair 2: Change Support Level to given Value for all Support Pairs", default=0)
	parser.add_argument('-i', '--Input_Filepath',
		action="store", dest="Input_Filepath",
		help="Path for Input Savegame", default="", required=True)
	parser.add_argument('-o', '--Output_Filepath',
		action="store", dest="Output_Filepath",
		help="Path for Output (Patched) Savegame", default="", required=True)
	parser.add_argument('-p', '--Support_Pair',
		action="store", dest="Support_Pair",
		help="Support Pair if --Support_Action 1 is used", default="")
	parser.add_argument('-SL', '--Support_level',
		action="store", dest="Support_level",
		help="Changes Support Level without Dialoge, if --Support_Action 2 is used", default=3)
	parser.add_argument('-SDL', '--Support_Dialoge_value',
		action="store", dest="Support_Dialoge_value",
		help="Changes Support Dialoge Value to Number given", default="ND")
	parser.add_argument('-HS','--Highest_Support_Dialoge', action='store_true', help="Highest Support Dialoge for Selected Supports")
	
	args = parser.parse_args()
	if args.Highest_Support_Dialoge:
		args.Support_Dialoge_value = "HD"

	Paaring_Name = ""	
	if args.Support_Pair != "":	
		Paaring_Name = Get_Support_Paaring(args.Support_Pair)

	if Paaring_Name == False:
		sys.exit("Cannot find Paaring: Is input correctly formatted ?")

	Support_Options(args.Input_Filepath, args.Output_Filepath, args.Change_Support_Action, args.Support_level, args.Support_Dialoge_value, Paaring_Name)