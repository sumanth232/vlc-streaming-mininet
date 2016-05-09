#!/usr/bin/python
import sys
import time
import re
import os
# from threading import Thread

from os import listdir
from os.path import isfile, join
import subprocess
from subprocess import STDOUT

refDir = '/home/sumanth/sample'
outDir = '/home/sumanth/teststorage/congest_10mb_link'
tempDir = '/home/sumanth/mininetDir/atemp_result_ssim'

inFiles = [f for f in listdir(refDir) if isfile(join(refDir, f))]
outFiles = [f for f in listdir(outDir) if isfile(join(outDir, f))]

ssimDict = {}

def storeSSIM_ShellCommand(outFilepath, refFilepath, tempFilepath):
	command = 'ffmpeg -i %s -i %s -filter_complex "ssim" "%s"'%(outFilepath, refFilepath, tempFilepath)


	# """ temp_result_filename should not be a full path from root /.  it should just be a simple name """
	# temp_result_filename = command.split()[-1].strip('"')
	# assert(temp_result_filename[0] != '/')
	# temp_result_filepath = join(os.getcwd(), temp_result_filename)
	# print temp_result_filepath


	if os.path.exists(tempFilepath):
		# print 'removing file - ', tempFilepath
		os.remove(tempFilepath)

	proc = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
	[stdout, stderr] = proc.communicate()
	returncode = proc.returncode

	if returncode != 0:  # There should be no errors in running the above command
		print 'RETURNCODE != 0 -> ssim FAILED for %s, %s'%(refFilepath, outFilepath)
		return

	# print stderr

	for line in stderr.splitlines():
		if 'Parsed_ssim' in line:
			print line
			m = re.search('All:(.+?) \(', line)

			try:
				ssim = float(m.group(1))
				# print 'ssim =', ssim
				# return ssim
				ssimDict[outFilepath.split('/')[-1]] = ssim
				print 'ssim success !!!'
				return

			except:
				# print "Unexpected error:", sys.exc_info()[0]
				# raise
				print 'ssim FAILED for %s, %s'%(refFilepath, outFilepath)
			
			break

	assert(False)



# def getSSIM(referenceFilepath, outputFilepath):

threads = []

for output in outFiles:

	# only consider mp4 files
	if output.split('.')[-1] != 'mp4':
		continue

	for ref in inFiles:
		if ref.split('.')[-1] != 'mp4':
			continue


		if output.split('.')[0].startswith(ref.split('.')[0]):
			outFilepath = join(outDir, output)
			refFilepath = join(refDir, ref)
			tempFilepath = join(tempDir, 'temp_'+output)

			# storeSSIM_ShellCommand(outFilepath, refFilepath, tempFilepath)
			# threads.append(Thread(target=storeSSIM_ShellCommand, args=(outFilepath, refFilepath, tempFilepath,) ))
			storeSSIM_ShellCommand(outFilepath, refFilepath, tempFilepath)

# """ Start all threads """
# for t in threads:
#     t.start()

# """ Wait for all of them to finish """
# for t in threads:
#     t.join()

# ssimDict = sorted(ssimDict.items())

for key,value in sorted(ssimDict.items()):
	print '%s\t%f'%(key,value)




# 			break

# result = subprocess.call('ffmpeg -i /home/sumanth/teststorage/test_10mb_link_h3_to_h4congest_4hosts.mp4 -i test.mp4 -filter_complex "ssim" "output_video.mp4"', shell=True)



# command = raw_input('enter command\n')
# print 'executing [%s]'%command
# exitcode = subprocess.call(command, shell=True, stderr=errfile, stdout=STDOUT)



# command = 'ffmpeg -i /home/sumanth/teststorage/test_10mb_link_h1_to_h2congest_4hosts.mp4 -i test.mp4 -filter_complex "ssim" "output_video.mp4"'
# proc = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
# exitcode = subprocess.call('ffmpeg -i /home/sumanth/teststorage/test_10mb_link_congest_4hosts.mp4 -i test.mp4 -filter_complex "ssim" "output_video.mp4"', shell=True)

# stdout = proc.communicate()[0]
# print 'STDOUT:{}'.format(stdout)

# [stdout, stderr] = proc.communicate()

# print 'STDout:[{}]'.format(stdout)
# print 'STDERR:[{}]'.format(stderr)
# print 'exitcode = ', proc.returncode

# execute_ssim_ShellCommand(command)
# print 'exitcode = ', exitcode



