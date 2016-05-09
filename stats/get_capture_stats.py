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


bash_script = '/home/sumanth/mininetDir/get_throughput_delay.sh'

refDir = '/home/sumanth/mininetDir/testing/testVideos'
outDir = '/home/sumanth/mininetDir/testing/savedStreams'

inFiles = [f for f in listdir(refDir) if isfile(join(refDir, f))]
traceFiles = [f for f in listdir(outDir) if isfile(join(outDir, f))]

# print inFiles


bitrateDict = {}
durationDict = {}

def getCaptureStats(srcIP, dstIP, port, outFilepath):
	# print srcIP, dstIP, port, outFilepath

	command = 'bash %s %s %s %s %s'%(bash_script, outFilepath, srcIP, dstIP, port)

	
	proc = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
	[stdout, stderr] = proc.communicate()
	returncode = proc.returncode

	if returncode != 0:  # There should be no errors in running the above command
		print 'RETURNCODE != 0 -> getCaptureStats FAILED'
		assert(False)
		return

	stdout = stdout.strip()
	# print stdout
	[bitrate, duration] = map(float, stdout.split(':'))

	bitrateDict[outFilepath.split('/')[-1]] = bitrate
	durationDict[outFilepath.split('/')[-1]] = duration

	

	



for output in traceFiles:

	# only consider pcap trace files
	if output.split('.')[-1] != 'pcap':
		continue

	for ref in inFiles:
		if ref.split('.')[-1] != 'mp4':
			continue


		if output.split('.')[0].startswith(ref.split('.')[0]):
			outFilepath = join(outDir, output)
			refFilepath = join(refDir, ref)

			lis = output.split('_')
			srcIP = '10.0.0.%d'%(int(lis[4].split('h')[1]))
			dstIP = '10.0.0.%d'%(int(lis[6].split('h')[1]))
			port = 5004
			getCaptureStats(srcIP, dstIP, port, outFilepath)

# """ Start all threads """
# for t in threads:
#     t.start()

# """ Wait for all of them to finish """
# for t in threads:
#     t.join()

# ssimDict = sorted(ssimDict.items())


print '\nBITRATE'
for key,value in sorted(bitrateDict.items()):
	print '%s\t%f'%(key,value)


print '\nDURATION'
for key,value in sorted(durationDict.items()):
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



