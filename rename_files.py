
import argparse
import os
import glob
import shutil

if __name__ == '__main__':

    	parser = argparse.ArgumentParser(description = "Rename Files")
    	parser.add_argument('--ribbon',nargs=1,help='4 digit ribbon number string',type=str)
    	parser.add_argument('--ch',nargs=1,help="Channel",type=str)
	parser.add_argument('--oldch',nargs=1,help='Old/wrong channel',type=str)
    	args = parser.parse_args()

	ribbon = args.ribbon[0]
	rootdir = "/nas2/data/M270907_Scnn1aTg2Tdt_13"
	str = rootdir+"/raw/data_extra/Ribbon%s/session01/MBP/*"%ribbon
	filelist = glob.glob(str)

	for f in filelist:
			ch = args.ch[0]
			oldch = args.oldch[0]
			dirinp = rootdir + "/raw/data_extra/Ribbon%s/session01/%s/"%(ribbon,ch)
			dirout = rootdir + "/raw/data/Ribbon%s/session01/%s/"%(ribbon,ch)

			if not os.path.exists(dirout):
				os.mkdir (dirout)
        		[L,sep,R] = f.rpartition('_S')
			[sectnum,sep1,R1] = R.partition('_F')
			newsectnum = int (sectnum) 
			sectnum = int(sectnum)
			filename = "%s%s%s%04d%s%s"%(dirinp,oldch,sep,sectnum,sep1,R1)
			newfilename = "%s%s%s%04d%s%s"%(dirout,ch,sep,newsectnum,sep1,R1)
			print filename
			print newfilename
			print "\n"
			shutil.copyfile(filename,newfilename)





