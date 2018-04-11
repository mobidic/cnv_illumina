##!/usr/local/bin/ python3.5
# coding: utf-8

# ==============================================================================

### IMPORT LIBRARIES
import sys		# system command
import csv		# read, write csv
import re		# regex
import argparse	# for options
import os		# for options
import pprint   # print data structure
import numpy as np
import math
import xlsxwriter
#from operator import itemgetter

# ==============================================================================

pp = pprint.PrettyPrinter(indent=4, depth=6)
#added david 27/03/2018 - deal with path passed as arg
parser = argparse.ArgumentParser(description='deal with path.')
parser.add_argument('-p', '--path', default='.')
parser.add_argument('-g', '--genelist', default='')
parser.add_argument('-t', '--type', default='tsv')
parser.add_argument('-o', '--out', default='cnv_analysis_sorted.xlsx')
args = parser.parse_args()
#print(args.path)
#sys.exit()
#Path = "/Users/david/Downloads/henri_cnv/03_2018/170925H27JNL/"
Path = args.path
Panel = args.genelist
Type = args.type
OutFile = args.out
ext = "tsv"
delim = "\t"
if Type == "csv":
	ext = "csv"
	delim = ","
if Panel == '':
	Panel = False

filelist = os.listdir(Path)
number_of_file = 0
sample_name = []
counter = 0
dict_regions = {}
dict_patients = {}
dict_mean = {}
total_mean = 0
dict_regions_ChrX = {}
dict_patients_ChrX = {}
total_mean_ChrX = 0
counter_ChrX = 0
print("\nFiles that will be considered:\n")


def build_dict(baseName, line, counter, dict_r, dict_p):
	if(baseName not in dict_p):
		dict_p[baseName] = {"sum_patient": float(line[4])}
	else:
		dict_p[baseName]["sum_patient"] += float(line[4])
	# création dictionnaire avec les valeurs bruts
	coordinate = (line[0],line[1],line[2], line[3])
	if coordinate not in dict_r :
		counter += 1
		dict_r[coordinate] = {baseName : {"brut" : float(line[4])}}
	else :
		dict_r[coordinate][baseName] = {"brut" : float(line[4])}	
	return(counter, dict_r, dict_p)

#############
for i in filelist:
	#### à fonctionnariser
	regex = re.compile(r'^([^\.].+)[\._]coverage\.%s$'%ext)
	matchObj = regex.search(os.path.basename(i))
	if(matchObj):
	#if i.endswith("coverage." + ext):  # You could also add "and i.startswith('f')
		print(i)
		number_of_file += 1
	#	regex = re.compile(r'^[^\.](.+)[\._]coverage\.[tc]sv$')
	#	matchObj = regex.search(os.path.basename(i))
	#	if(matchObj):
		baseName = matchObj.group(1)
		sample_name.append(baseName)
	#	else:
	#		sys.exit("Error [1] : file \'" + i + "\' does not respect format (sample.coverage.tsv).")
	####

		with open(Path + i, 'r') as csvfile:
			csvreader = csv.reader(csvfile, delimiter =delim)
			for line in csvreader:
				line = [w.replace(',', '.') for w in line]
				expression = r'^.*#.*$' # remove header
				if not re.match(expression, line[0]) and line[0] != "chrX" and line[0] != "chrY":
					(counter, dict_regions, dict_patients) = build_dict(baseName, line, counter, dict_regions, dict_patients)
					#création moyenne par patient
					#if(baseName not in dict_patients):
					#	dict_patients[baseName] = {"sum_patient": float(line[4])}
					#else:
					#	dict_patients[baseName]["sum_patient"] += float(line[4])
					# création dictionnaire avec les valeurs bruts
					#coordinate = (line[0],line[1],line[2], line[3])
					#if coordinate not in dict_regions :
					#	counter += 1
					#	dict_regions[coordinate] = {baseName : {"brut" : float(line[4])}}
					#else :
					#	dict_regions[coordinate][baseName] = {"brut" : float(line[4])}
				else :
					if not re.match(expression, line[0]) and line[0] == "chrX":
						(counter_ChrX, dict_regions_ChrX, dict_patients_ChrX) = build_dict(baseName, line, counter_ChrX, dict_regions_ChrX, dict_patients_ChrX)
						# if(baseName not in dict_patients_ChrX):
						# 	dict_patients_ChrX[baseName] = {"sum_patient": float(line[4])}
						# else:
						# 	dict_patients_ChrX[baseName]["sum_patient"] += float(line[4])
						# # création dictionnaire avec les valeurs bruts
						# coordinate = (line[0],line[1],line[2],line[3])
						# if coordinate not in dict_regions_ChrX :
						# 	counter_ChrX += 1
						# 	dict_regions_ChrX[coordinate] = {baseName : {"brut" : float(line[4])}}
						# else :
						# 	dict_regions_ChrX[coordinate][baseName] = {"brut" : float(line[4])}
# faire pareil pour ChrY
#############

#############

# Itération sur le dictionnaire patient pour calculer la moyenne par  patient

# def sample_mean(dico):
# 	for sample_name in dict_patients:

for sample_name in dict_patients:
		dict_patients[sample_name]["moyenne_patient"] = dict_patients[sample_name]["sum_patient"]/ counter
# FOR X
for sample_name in dict_patients_ChrX:
		dict_patients_ChrX[sample_name]["moyenne_patient"] = dict_patients_ChrX[sample_name]["sum_patient"]/ counter_ChrX

#############
# Itération sur le dictionnaire patient pour calculer la moyenne par exon et l'exon normalisé

def exon_mean(dict_r, dict_m):
	for coordinate in dict_r :
		for sample_name in dict_r[coordinate]:
			total = 0
			full_total = 0
			sample_number = 0
			for sample_other in dict_r[coordinate]:
				if sample_other != sample_name:
					total += dict_r[coordinate][sample_other]['brut']
					sample_number +=1
				full_total += dict_r[coordinate][sample_other]['brut']
			#moyenne_exon = total / sample_number
			dict_m[coordinate] = {"exon_mean_doc": float(full_total / (sample_number+1))}
			dict_r[coordinate][sample_name]["moyenne_exon"] = float(total / sample_number)
	return(dict_r, dict_m)

(dict_regions, dict_mean) = exon_mean(dict_regions, dict_mean)
(dict_regions_ChrX, dict_mean) = exon_mean(dict_regions_ChrX, dict_mean)

#pp.pprint(dict_regions)

# for coordinate in dict_regions :
# 	for sample_name in dict_regions[coordinate]:
# 		total = 0
# 		full_total = 0
# 		sample_number = 0
# 		for sample_other in dict_regions[coordinate]:
# 			if sample_other != sample_name:
# 				total += dict_regions[coordinate][sample_other]['brut']
# 				sample_number +=1
# 			full_total += dict_regions[coordinate][sample_other]['brut']
# 		moyenne_exon = total / sample_number
# 		dict_mean[coordinate] = {"exon_mean_doc": full_total / (sample_number+1)}
# 		dict_regions[coordinate][sample_name]["moyenne_exon"] = float(moyenne_exon)
# 
# # FOR X
# for coordinate in dict_regions_ChrX :
# 	for sample_name in dict_regions_ChrX[coordinate]:
# 		total = 0
# 		full_total = 0
# 		sample_number = 0
# 		for sample_other in dict_regions_ChrX[coordinate]:
# 			if sample_other != sample_name:
# 				total += dict_regions_ChrX[coordinate][sample_other]['brut']
# 				sample_number +=1
# 			full_total += dict_regions_ChrX[coordinate][sample_other]['brut']
# 		moyenne_exon = total / sample_number
# 		dict_mean[coordinate] = {"exon_mean_doc": full_total / (sample_number+1)}
# 		dict_regions_ChrX[coordinate][sample_name]["moyenne_exon"] = float(moyenne_exon)

#############
# Itération sur le dictionnaire régions pour calculer la somme moyenne par patient
# sauf pour les exons du patient - Somme ajoutée dans le dict patients
for sample_name in dict_patients:
	dict_patients[sample_name]["somme_moyenne_exon"] = 0
	for coordinate in dict_regions :
		dict_patients[sample_name]["somme_moyenne_exon"] += dict_regions[coordinate][sample_name]["moyenne_exon"]
	dict_patients[sample_name]["total_mean_sans_le_patient"] = dict_patients [sample_name]["somme_moyenne_exon"] / counter
#for sample_name in dict_patients:
#	dict_patients[sample_name]["total_mean_sans_le_patient"] = dict_patients [sample_name]["somme_moyenne_exon"] / counter

# FOR X
for sample_name in dict_patients_ChrX:
	dict_patients_ChrX[sample_name]["somme_moyenne_exon"] = 0
	for coordinate in dict_regions_ChrX :
		dict_patients_ChrX[sample_name]["somme_moyenne_exon"] += dict_regions_ChrX[coordinate][sample_name]["moyenne_exon"]
	dict_patients_ChrX[sample_name]["total_mean_sans_le_patient"] = dict_patients_ChrX [sample_name]["somme_moyenne_exon"] / counter_ChrX

#for sample_name in dict_patients_ChrX:
#	dict_patients_ChrX[sample_name]["total_mean_sans_le_patient"] = dict_patients_ChrX [sample_name]["somme_moyenne_exon"] / counter_ChrX

#############
# Itération sur le dictionnaire régions pour ajouter la valeur "exon_normalise"
# Moyenne exon / Moyenne tota
#@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@
for sample_name in dict_patients:
	for coordinate in dict_regions :
		dict_regions [coordinate][sample_name]["exon_normalise"] = dict_regions[coordinate][sample_name]["moyenne_exon"] / dict_patients[sample_name]["total_mean_sans_le_patient"]

# FOR X

for sample_name in dict_patients_ChrX:
	for coordinate in dict_regions_ChrX :
		dict_regions_ChrX [coordinate][sample_name]["exon_normalise"] = dict_regions_ChrX[coordinate][sample_name]["moyenne_exon"] / dict_patients_ChrX[sample_name]["total_mean_sans_le_patient"]



#############
# Normalisation par patient : valeur couverture exon / moyenne patient

for coordinate in dict_regions :
	for sample_name in dict_regions[coordinate]:
		patient_normalise = dict_regions[coordinate][sample_name]['brut'] / dict_patients[sample_name]["moyenne_patient"]
		dict_regions[coordinate][sample_name]["patient_normalise"] = float(patient_normalise)

# FOR X

for coordinate in dict_regions_ChrX :
	for sample_name in dict_regions_ChrX[coordinate]:
		patient_normalise = dict_regions_ChrX[coordinate][sample_name]['brut'] / dict_patients_ChrX[sample_name]["moyenne_patient"]
		dict_regions_ChrX[coordinate][sample_name]["patient_normalise"] = float(patient_normalise)

#############

# Calcul ratio normalise

for coordinate in dict_regions :
	for sample_name in dict_regions[coordinate]:
		try :
			ratio_normalise = float(dict_regions[coordinate][sample_name]["patient_normalise"]) / float(dict_regions[coordinate][sample_name]["exon_normalise"])
		except ZeroDivisionError :
			ratio_normalise = float(0)
		dict_regions[coordinate][sample_name]["ratio_normalise"] = float(ratio_normalise)
# FOR X
for coordinate in dict_regions_ChrX :
	for sample_name in dict_regions_ChrX[coordinate]:
		try :
			ratio_normalise = float(dict_regions_ChrX[coordinate][sample_name]["patient_normalise"]) / float(dict_regions_ChrX[coordinate][sample_name]["exon_normalise"])
		except ZeroDivisionError :
			ratio_normalise = float(0)
		dict_regions_ChrX[coordinate][sample_name]["ratio_normalise"] = float(ratio_normalise)

#pp.pprint(dict_patients)
#pp.pprint(dict_regions)
#dict_regions_sorted = sorted(dict_regions, key=lambda row:(row[0],row[1]), reverse=False)
#dict_regions_sorted = sorted(dict_regions, key=itemgetter(0,1))

with open('cnv_analysis.txt', 'w') as csv_file:
	writer = csv.writer(csv_file)
	header = "Chr\tStart\tEnd\tRegionID\tMean DoC\t"
	for coordinate in dict_regions :
		for sample_name in dict_regions[coordinate]:
			header += str(sample_name) + "_brut" + "\t"
		for sample_name in dict_regions[coordinate]:
			header += str(sample_name) + "_moy_exon" + "\t"
		for sample_name in dict_regions[coordinate]:
			header += str(sample_name) + "_patient_normalise" + "\t"
		for sample_name in dict_regions[coordinate]:
			header += str(sample_name) + "_exon_normalise" + "\t"
		for sample_name in dict_regions[coordinate]:
			header += str(sample_name) + "_ratio" + "\t"
		break
	csv_file.write(header + "\n")
	for coordinate in dict_regions :
		csv_file.write(
			str(coordinate[0]) + "\t" +
			str(coordinate[1]) + "\t" +
			str(coordinate[2]) + "\t" +
			str(coordinate[3]) + "\t" +
			str(round(dict_mean[coordinate]["exon_mean_doc"], 2)) + "\t"
			)
		for sample_name in dict_regions[coordinate] :
			csv_file.write(str(dict_regions[coordinate][sample_name]["brut"]) + "\t")
		for sample_name in dict_regions[coordinate] :
			csv_file.write(str(round(dict_regions[coordinate][sample_name]["moyenne_exon"], 2)) + "\t")
		for sample_name in dict_regions[coordinate] :
			csv_file.write(str(round(dict_regions[coordinate][sample_name]["patient_normalise"],2)) + "\t")
		for sample_name in dict_regions[coordinate] :
			csv_file.write(str(round(dict_regions[coordinate][sample_name]["exon_normalise"],2)) + "\t")
		for sample_name in dict_regions[coordinate] :
			csv_file.write(str(round(dict_regions[coordinate][sample_name]["ratio_normalise"],3)) + "\t")
		csv_file.write("\n")

with open('cnv_analysis_ChrX.txt', 'w') as csv_file:
	writer = csv.writer(csv_file)
	header = "Chr\tStart\tend\tRegionID\tMean DoC\t"
	for coordinate in dict_regions_ChrX :
		for sample_name in dict_regions_ChrX[coordinate]:
			header += str(sample_name) + "_brut" + "\t"
		for sample_name in dict_regions_ChrX[coordinate]:
			header += str(sample_name) + "_moy_exon" + "\t"
		for sample_name in dict_regions_ChrX[coordinate]:
			header += str(sample_name) + "_patient_normalise" + "\t"
		for sample_name in dict_regions_ChrX[coordinate]:
			header += str(sample_name) + "_exon_normalise" + "\t"
		for sample_name in dict_regions_ChrX[coordinate]:
			header += str(sample_name) + "_ratio" + "\t"
		break
	csv_file.write(header + "\n")
	for coordinate in dict_regions_ChrX :
		csv_file.write(
			str(coordinate[0]) + "\t" +
			str(coordinate[1]) + "\t" +
			str(coordinate[2]) + "\t" +
			str(coordinate[3]) + "\t" +
			str(round(dict_mean[coordinate]["exon_mean_doc"], 2)) + "\t"
			)
		for sample_name in dict_regions_ChrX[coordinate] :
			csv_file.write(str(dict_regions_ChrX[coordinate][sample_name]["brut"]) + "\t")
		for sample_name in dict_regions_ChrX[coordinate] :
			csv_file.write(str(round(dict_regions_ChrX[coordinate][sample_name]["moyenne_exon"], 2)) + "\t")
		for sample_name in dict_regions_ChrX[coordinate] :
			csv_file.write(str(round(dict_regions_ChrX[coordinate][sample_name]["patient_normalise"],2)) + "\t")
		for sample_name in dict_regions_ChrX[coordinate] :
			csv_file.write(str(round(dict_regions_ChrX[coordinate][sample_name]["exon_normalise"],2)) + "\t")
		for sample_name in dict_regions_ChrX[coordinate] :
			csv_file.write(str(round(dict_regions_ChrX[coordinate][sample_name]["ratio_normalise"],3)) + "\t")
		csv_file.write("\n")

# Sorting files, works on Mac only, if you are poor (like Charles) with other OS, go fuck yourself
os.system("sort -k1.4n -k2,2n -k3,3n cnv_analysis.txt > cnv_analysis_sorted.txt")
os.system("sort -k1.4n -k2,2n -k3,3n cnv_analysis_ChrX.txt > cnv_analysis_ChrX_sorted.txt")
#



###########
if (Panel != False):
	panel = open(Panel, 'r')
	# panelreader = csv.DictReader(panel, delimiter='\t')

	liste_panel = []
	for gene in panel :
		liste_panel.append(gene.rstrip())
###########


### Excel convertion


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
workbook = xlsxwriter.Workbook(OutFile)
#Define style of cells
style1 = workbook.add_format({'bold': True, 'bg_color': '#FFC25E', 'locked' : True})
style2 = workbook.add_format({'bold': True, 'bg_color': '#FF3333', 'locked' : True})
style3 = workbook.add_format({'bold': True, 'bg_color': '#5EBBFF', 'locked' : True})
style4 = workbook.add_format({'bold': True, 'bg_color': '#8F5EFF', 'locked' : True})
style5 = workbook.add_format({'bold': True, 'locked' : True})
#http://xlsxwriter.readthedocs.io/example_conditional_format.html#ex-cond-format
# Add a format. Light red fill with dark red text.
format1 = workbook.add_format({'bg_color': '#FFC7CE',
                               'font_color': '#9C0006'})
# Add a format. Green fill with dark green text.
format2 = workbook.add_format({'bg_color': '#C6EFCE',
                               'font_color': '#006100'})
#worksheet summary to get only interesting stuff
summary = workbook.add_worksheet('Summary')
summary.freeze_panes(1, 5)
summary.set_row(0, 20, style5)
summary.set_column('A:E', 15, style5)
summary.set_column('D:D', 25)
if (Panel != False):
	worksheet2 = workbook.add_worksheet(str("Panel"))
	worksheet2.freeze_panes(1, 5)
	worksheet2.set_row(0, 20, style5)
	worksheet2.set_column('A:E', 15, style5)
	worksheet2.set_column('D:D', 25)

def add_conditionnal_format(worksheet, threshold, start, end):
	#add a conditionnal format to raw DoC
	if (start == 0):
		start = 2
	cell_range = "E" + str(start) + ":T" + str(end)
	worksheet.conditional_format(cell_range, {'type': 'cell',
                                         'criteria': '>=',
                                         'value': threshold,
                                         'format': format2})
	worksheet.conditional_format(cell_range, {'type': 'cell',
                                         'criteria': '<',
                                         'value': threshold,
                                         'format': format1})

def writing_total(worksheet, txt_file, threshold_del_hmz, threshold_del_htz, threshold_dup_htz, threshold_dup_hmz, start1=0, start2=0):
	# TODO: change it to parameter and save worksheet
	# if panel:

	worksheet = workbook.add_worksheet(str(worksheet))
	worksheet.freeze_panes(1, 5)
	worksheet.set_row(0, 20, style5)
	worksheet.set_column('A:E', 15, style5)
	worksheet.set_column('D:D', 25)
	#structure data from txt
	f = open( str(txt_file), 'r+')
	row_list = []
	for row in f:
		row_list.append(row.split('\t'))
	# pp.pprint(row_list)

	column_list = zip(*row_list)
	column_list2 = zip(*row_list)
	column_list3 = zip(*row_list)
	i = 0
	l = 0
	interesting = []
	gene4interest = []
	regex_ratio = re.compile(r'(.*)_ratio$')
	regex_noCNV = re.compile(r'no CNV')
	regex_region = re.compile(r'RegionID')
	for column in column_list:
		for item in range(len(column)):
			if regex_region.search(column[0]):
				if (Panel != False):
					for gene in liste_panel:
						if re.compile(r'.*' + gene + '.*').search(column[item]) :
							# print (column[item])
							gene4interest.append(item)
				else:
					gene4interest.append(item)
			if regex_ratio.search(column[0]):
				if (item > 0) :
					if(float(column[item]) <= threshold_del_hmz):
						worksheet.write(item, i , column[item],style1)
						for k in range(item-1,item+2):
							if (k > 0):
								interesting.append(k)
					elif(float(column[item]) <= threshold_del_htz):
						worksheet.write(item, i, column[item],style2)
						for k in range(item-1,item+2):
							if (k > 0):
								interesting.append(k)
					elif(float(column[item]) <= threshold_dup_htz):
						worksheet.write(item, i, column[item], style5)
					elif(float(column[item]) <= threshold_dup_hmz):
						worksheet.write(item, i, column[item],style3)
						for k in range(item-1,item+2):
							if (k > 0):
								interesting.append(k)
					else :
						worksheet.write(item, i, column[item],style4)
						for k in range(item-1,item+2):
							if (k > 0):
								interesting.append(k)
				else:
					worksheet.write(item, i, column[item], style5)
			else:
				worksheet.write(item,i,column[item])
			if (item == 0):
				summary.write(item,i,column[item], style5)
				# if panel:
				if (Panel != False):
					worksheet2.write(item,i,column[item], style5)
		i+=1
	i = 0
	uniq_interesting = list(set(interesting))
	for column in column_list2:
		j = 0
		if(start1 > 0):
			j = start1
		for item in range(len(column)):
			if (item in uniq_interesting):
				if regex_ratio.search(column[0]):
					if(item > 0):
						if(float(column[item]) <= threshold_del_hmz):
							summary.write(j, i , column[item],style1)
						elif(float(column[item]) <= threshold_del_htz):
							summary.write(j, i, column[item],style2)
						elif(float(column[item]) <= threshold_dup_htz):
							summary.write(j, i, column[item], style5)
						elif(float(column[item]) <= threshold_dup_hmz):
							summary.write(j, i, column[item],style3)
						else :
							summary.write(j, i, column[item],style4)
					else:
						summary.write(j, i, column[item], style5)
				else:
					summary.write(j,i,column[item])
				j+=1
		i+=1
	

	i = 0
	# part to dev
	if (Panel != False):
		#l=0
		uniq_interesting_panel = list(set(gene4interest))
		for column in column_list3:
			l = 1
			if (start2 != 0 ):
				l = start2
			for item in range(len(column)):
				if (item in uniq_interesting_panel):
					if regex_ratio.search(column[0]):
						if(item > 0):
							if(float(column[item]) <= threshold_del_hmz):
								worksheet2.write(l, i , column[item],style1)
							elif(float(column[item]) <= threshold_del_htz):
								worksheet2.write(l, i, column[item],style2)
							elif(float(column[item]) <= threshold_dup_htz):
								worksheet2.write(l, i, column[item], style5)
							elif(float(column[item]) <= threshold_dup_hmz):
								worksheet2.write(l, i, column[item],style3)
							else :
								worksheet2.write(l, i, column[item],style4)
						else:
							worksheet2.write(l, i, column[item], style5)
					else:
						worksheet2.write(l,i,column[item])
					l+=1
			i+=1
		i = 0
		worksheet2.set_column('F:BM', None, None, {'level': 1, 'hidden': True})
		add_conditionnal_format(worksheet2, 50, start2, start2 + len(gene4interest))
	worksheet.set_column('F:BM', None, None, {'level': 1, 'hidden': True})
	add_conditionnal_format(worksheet, 50, 2, len(row_list))
	worksheet.protect()
	summary.set_column('F:BM', None, None, {'level': 1, 'hidden': True})
	add_conditionnal_format(summary, 50, start1, start1 + len(uniq_interesting))
	return (j,l)

#worksheet for autosomes
(start1, start2) = writing_total('Autosomes','cnv_analysis.txt', 0.3, 0.7, 1.3, 1.7)
# print (start1, start2)
#worksheet for ChrX
writing_total('Chromosome_X','cnv_analysis_ChrX_sorted.txt', 0.3, 0.7, 1.3, 1.7, start1, start2)
worksheet2.protect()
summary.protect()
workbook.close()
#remove temporary files
os.system("rm cnv_analysis.txt cnv_analysis_sorted.txt cnv_analysis_ChrX.txt cnv_analysis_ChrX_sorted.txt")
print("\nDone!!!\n")
