import sys, os
import xlsxwriter
from os.path import isfile, join

rootDir = os.path.realpath('..')

sd_flow_filepath = join(rootDir, 'testVideos/360x240_2mb.mp4')
hd_flow_filepath = join(rootDir, 'testVideos/720x480_5mb.mp4')

sd_filename = os.path.basename(sd_flow_filepath)
hd_filename = os.path.basename(hd_flow_filepath)

qos_result_file = join(rootDir, 'stats/manual_written_results/ssim_results_qos_10mb_link.txt')
congest_result_file = join(rootDir, 'stats/manual_written_results/ssim_results_qos_10mb_link.txt')

qos_bitrate_result_file = join(rootDir, 'stats/manual_written_results/qos_capture_stats_bitrate.txt')
qos_duration_result_file = join(rootDir, 'stats/manual_written_results/qos_capture_stats_packetDelay.txt')
congest_bitrate_result_file = join(rootDir, 'stats/manual_written_results/congest_capture_stats_bitrate.txt')
congest_duration_result_file = join(rootDir, 'stats/manual_written_results/qos_capture_stats_bitrate.txt')

excelFilesDir = join(rootDir, 'stats/generated_excel_sheet')


# RESULT_file = qos_bitrate_result_file


max_hosts_count = 32

def print_to_existing_excel_worksheet(titlestr,qosDict, congestDict, worksheet, row, clm):

	# Widen the first column to make the text clearer.
	worksheet.set_column('%s:%s'%(chr(ord('A')+clm+1), chr(ord('A')+clm+1)), 11)
	worksheet.set_column('%s:%s'%(chr(ord('A')+clm+2), chr(ord('A')+clm+2)), 13)

	worksheet.write(row, clm, titlestr)
	row += 1
	worksheet.write(row, clm, 'Hosts')
	worksheet.write(row, clm+1, '240p with QoS')
	worksheet.write(row, clm+2, '240p without QoS')
	row += 1

	for key in [4,8,12,16,20,24,28,32]:
		worksheet.write(row, clm, key)
		worksheet.write(row, clm+1, qosDict[key][0])  # 0 for sd, 1 for hd
		worksheet.write(row, clm+2, congestDict[key][0])
		row += 1


	row += 6

	worksheet.write(row, clm, titlestr)
	row += 1
	worksheet.write(row, clm, 'Hosts')
	worksheet.write(row, clm+1, '480p with QoS')
	worksheet.write(row, clm+2, '480p without QoS')
	row += 1
	for key in [4,8,12,16,20,24,28,32]:
		worksheet.write(row, clm, key)
		worksheet.write(row, clm+1, qosDict[key][1])  # 0 for sd, 1 for hd
		worksheet.write(row, clm+2, congestDict[key][1])
		row += 1

def print_to_excel(outExcelFilepath):
	# Create an new Excel file and add a worksheet.
	workbook = xlsxwriter.Workbook(outExcelFilepath)
	worksheet = workbook.add_worksheet()

	print_to_existing_excel_worksheet('BITRATE', qos_bitrate_dict, congest_bitrate_dict, worksheet, 2,0)
	print_to_existing_excel_worksheet('BITRATE', qos_bitrate_dict, congest_bitrate_dict, worksheet, 2,0)

	print_to_existing_excel_worksheet('PACKETDELAY', qos_duration_dict, congest_duration_dict, worksheet, 2,6)
	print_to_existing_excel_worksheet('PACKETDELAY', qos_duration_dict, congest_duration_dict, worksheet, 2,6)

	workbook.close()


def storessim_for_nhosts(content, mydict, n):
	sd_ssim = []
	hd_ssim = []

	for line in content:
		# if it is a valid ssim score line
		if 'FAILED' not in line and '_%dhosts'%n in line:
			if sd_filename.split('.')[0] in line:
				sd_ssim.append(float(line.split('\t')[-1]))
			elif hd_filename.split('.')[0] in line:
				hd_ssim.append(float(line.split('\t')[-1]))
			else:
				raise ValueError('Invalid file name error !')

	sd_ssim_avg = sum(sd_ssim)/float(len(sd_ssim))
	hd_ssim_avg = sum(hd_ssim)/float(len(hd_ssim))

	mydict[n] = (sd_ssim_avg, hd_ssim_avg)
	# print mydict


def get_ssim_stats(result_filepath):
	mydict = {}

	with open(result_filepath) as f:
		content = f.readlines()

	for i in range(max_hosts_count/4 + 1)[1:]:
		n = i*4
		storessim_for_nhosts(content, mydict, n)

	return mydict

qos_bitrate_dict = get_ssim_stats(qos_bitrate_result_file)
congest_bitrate_dict = get_ssim_stats(congest_bitrate_result_file)

qos_duration_dict = get_ssim_stats(qos_duration_result_file)
congest_duration_dict = get_ssim_stats(congest_duration_result_file)


print_to_excel(join(excelFilesDir,'bitrate_packetDelay.xlsx'))


# print ssim_dict
# for key, value in sorted(ssim_dict.items()):
# 	print '%d\t(%0.6f, %0.6f)'%(key, value[0], value[1])


