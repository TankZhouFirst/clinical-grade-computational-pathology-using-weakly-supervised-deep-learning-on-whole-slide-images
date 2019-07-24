from __future__ import print_function
import sys
import os
from azure.storage.blob import BlockBlobService

# azure container
sas_token='?sv=2018-03-28&ss=b&srt=so&sp=rl&se=2019-07-28T08:52:42Z&st=2019-06-28T00:52:42Z&spr=https&sig=o%2F5t40kYxt3pLXfwBa9NZFm1PJJvExhWOergB0R%2Bw4I%3D'
service='publicresearchdata'
container='2019-campanella-nature-medicine'
# files to download
files = ['target.csv','README.txt','HobI18-323369624610.svs','HobI18-331819024579.svs','HobI18-386778904831.svs','HobI18-406340937735.svs','HobI18-423802432924.svs','HobI18-494717903184.svs','HobI18-522858288490.svs','HobI18-559324358086.svs','HobI18-585178062343.svs','HobI18-593216593303.svs','HobI18-595961947225.svs','HobI18-615488176850.svs','HobI18-618697230393.svs','HobI18-628416694544.svs','HobI18-641230701381.svs','HobI18-671727960719.svs','HobI18-685127433264.svs','HobI18-706116254954.svs','HobI18-711038761484.svs','HobI18-767451561893.svs','HobI18-789815111269.svs','HobI18-796881418672.svs','HobI18-987777882592.svs','HobI16-053768896760.svs','HobI16-072823783181.svs','HobI16-105105202254.svs','HobI16-303757967057.svs','HobI16-334188031493.svs','HobI16-553454144783.svs','HobI16-568713100973.svs','HobI16-673050001795.svs','HobI16-708082515907.svs','HobI16-723628532151.svs','HobI16-732317408482.svs','HobI16-800515347962.svs','HobI16-837889994938.svs','HobI16-850322983160.svs','HobI17-014668898938.svs','HobI17-036398431404.svs','HobI17-054128333834.svs','HobI17-054246972264.svs','HobI17-074732741064.svs','HobI17-085745661307.svs','HobI17-092737210733.svs','HobI17-117814883069.svs','HobI17-158487016760.svs','HobI17-176780238278.svs','HobI17-188975055458.svs','HobI17-192632085422.svs','HobI17-203923657811.svs','HobI17-213453116848.svs','HobI17-219470745199.svs','HobI17-247547626174.svs','HobI17-255403409805.svs','HobI17-265070624026.svs','HobI17-269154319884.svs','HobI17-288509838143.svs','HobI17-313879325559.svs','HobI17-324909994030.svs','HobI17-334708419649.svs','HobI17-348600370849.svs','HobI17-377050210278.svs','HobI17-421574798660.svs','HobI17-425397955012.svs','HobI17-435966474961.svs','HobI17-440719796933.svs','HobI17-447409697483.svs','HobI17-458471686651.svs','HobI17-467062691081.svs','HobI17-476054943119.svs','HobI17-485538505474.svs','HobI17-495667251867.svs','HobI17-519774790910.svs','HobI17-545903287930.svs','HobI17-553581330459.svs','HobI17-558005179666.svs','HobI17-593769981242.svs','HobI17-622270352572.svs','HobI17-627940372723.svs','HobI17-636884305743.svs','HobI17-640264021539.svs','HobI17-648654794571.svs','HobI17-655346198230.svs','HobI17-659203035810.svs','HobI17-660006336651.svs','HobI17-677160798281.svs','HobI17-681327099314.svs','HobI17-688924862435.svs','HobI17-719246842170.svs','HobI17-719990954481.svs','HobI17-743356791372.svs','HobI17-749048090290.svs','HobI17-750867388324.svs','HobI17-778814457598.svs','HobI17-788882576662.svs','HobI17-792063748170.svs','HobI17-793253845164.svs','HobI17-796855272934.svs','HobI17-800973460562.svs','HobI17-804061080478.svs','HobI17-812250131208.svs','HobI17-828077018053.svs','HobI17-848084691666.svs','HobI17-875559163472.svs','HobI17-876230315187.svs','HobI17-883321793262.svs','HobI17-890038662634.svs','HobI17-929050186119.svs','HobI17-974235225863.svs','HobI17-977643406918.svs','HobI18-029043796428.svs','HobI18-029873239450.svs','HobI18-045092912528.svs','HobI18-069937884593.svs','HobI18-092641163539.svs','HobI18-099794757323.svs','HobI18-104537363663.svs','HobI18-116874549628.svs','HobI18-116913530563.svs','HobI18-155976821520.svs','HobI18-156692134456.svs','HobI18-160344775131.svs','HobI18-171355267698.svs','HobI18-173605056616.svs','HobI18-189221870743.svs','HobI18-244929700327.svs','HobI18-246204354838.svs','HobI18-264942777411.svs','HobI18-295854571047.svs','HobI18-303776291914.svs']

# 2/3 compatibility
try:
	input = raw_input
except:
	pass

def confirmDownload():
	"""
	confirm OK to download
	"""
	keys = input('This script will download 52.4GB to the current working directory. Proceed? [Y/N]...')
	valid = {'y', 'n'}
	if keys.lower() not in valid:
		print('invalid input. Please enter ''Y'' or ''N''')
	if keys.lower() != 'y':
		print('aborting')
		quit()


def main():
	"""
	download public dataset from azure blob storage container to current working directory
	"""
	confirmDownload()

	#connect to azure container
	blobservice = BlockBlobService(service,sas_token=sas_token)

	#download individual dataset files to current directory
	count_iter = 0
	failed_downloads = 0
	for f in files:
		count_iter = count_iter+1
		print('downloading {} (file {} of {})'.format(f, count_iter, len(files)))

		# download file, up to 3 times
		success=0
		tries=0
		while not success and tries < 3:
			try:
				blobservice.get_blob_to_path(container,f, f)
				success = 1
			except:
				print('failed to download {} on try {} of 3'.format(f, tries))
				tries = tries + 1
		# track failures
		if success == 0:
			failed_downloads = failed_downloads + 1

	# log completion & stats
	print('download complete...successfully downloaded {} of {} files'.format(len(files)-failed_downloads, len(files)))

if __name__ == '__main__':
    main()