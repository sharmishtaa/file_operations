#input, root directory of images
import argparse
import os
import convertmetadata
import numpy as np
import csv
import glob
import sys
import pandas as pd

print("\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create an up to date state file from a project directory in the Allen Directory format and upload the initial tilespecs to render")

    parser.add_argument('--projectDirectory', nargs='+', help="Path to the project directory.")
    parser.add_argument('--renderbaseUrl',nargs=1,help="host name of the render server",default="'http://ibs-forrestc-ux1:8080/render-ws/v1'")
    parser.add_argument('--renderOwner',nargs=1,help="name of project owner",default = "Forrest")
    parser.add_argument('--projectName',nargs=1,help="name of the project (default derived from project directory leaf directory)")
    parser.add_argument('--outputFile',nargs=1,help="output file name")
    parser.add_argument('--oneribbononly',nargs=1,help="process only one ribbon true/false",default = "False")
    parser.add_argument('--ribbon',nargs=1,help="ribbon number")


    args = parser.parse_args()
    projectDirectorylist = args.projectDirectory
    projectDirectory = args.projectDirectory[0]
    assert os.path.isdir(projectDirectory), "'"+projectDirectory + "' is not a valid directory"



    baseUrl = args.renderbaseUrl[0]
    owner = args.renderOwner[0]
    
    outputfile = args.outputFile[0]
    #if args.projectName is not None:
#	project = args.projectName
 #   else:
	#project = os.path.split(projectDirectory)[1]

    numdirs = len(projectDirectorylist)
    
    #check that project names are the same
    baseprojectname = os.path.split(projectDirectorylist[0])[1]
    
    
    for q in range(1,numdirs):
    	project = os.path.split(projectDirectorylist[q])[1]
	
        if project != baseprojectname:
		print "Project names are not the same!!!!"
		exit()
    
    
#output, state table ala bill karsh
#bill's format
#Z tileID a00 a01 a02 a10 a11 a12 col row cam full_path

#my format
#includes ribbon number, section number, session number, channel number
#tileID ribbon section frame a00 a01 a02 a10 a11 a12 session ch full_path
#tileID = ch + 1000*frame + 1000*1000*section + 1000*1000*1000*1000*ribbon + 1000*1000*1000*1000*100*session
# newer version now includes stage coordinates, session name, height, width, many other columns.
#pull out all the tif files that are subdirectories under this
tif_files=[]

#print numdirs
for p in range (0,numdirs):
	rootdir=os.path.join(projectDirectorylist[p],'raw','data')
	print rootdir
	for (dirpath, dirnames, filenames) in os.walk(rootdir):
		#print dirpath
		#print "THIS IS DIRPATH"
		#print dirnames
		#print filenames
		l = dirpath.split("Ribbon")
		if len(l) > 1:
			if args.oneribbononly[0]=="True":
				if l[1][:4] == args.ribbon[0]:
  					tif_files.extend([os.path.join(dirpath,f) for f in filenames if os.path.splitext(f)[1]=='.tif'])
			else:
				tif_files.extend([os.path.join(dirpath,f) for f in filenames if os.path.splitext(f)[1]=='.tif'])
Nfiles=len(tif_files)

print Nfiles



#get the unique channel names
ch_names=sorted(set([os.path.split(os.path.split(f)[0])[1] for f in tif_files]))
print "channels "
print ch_names
quit
print "\n"

#get the unique image session names

image_sessions = sorted(set([os.path.split(os.path.split(os.path.split(f)[0])[0])[1] for f in tif_files]))
print "imaging sessions:"
print image_sessions
print "\n"


dl = []
for filepath in tif_files:
    #the frame index
    [dir,fname]=os.path.split(filepath)

    d = {}
    d['full_path']=filepath
    #(prefix0,partRibbon,suffix0) = dir.partition('ribbon_')
    (prefix0,partRibbon,suffix0) = dir.partition('Ribbon')
    (ribbonstring,slash,suffix1)=suffix0.partition('/')

    d['ribbon']=int(ribbonstring)
    
    f=os.path.splitext(fname)[0]
    (f,part,frame1)=f.partition('_F')
    (sframe,part1,sz) = frame1.partition('_Z')  
    d['frame']=int(sframe)
    d['zstack']=int(sz)
    (f,part,section)=f.partition('_S')
    d['section']=int(section)

    #find the index for the channel
    ch_name=os.path.split(os.path.split(filepath)[0])[1]
    #  if 'DAPI_0' in ch_name.lower():

    [chnameprefix, sep, num] = ch_name.partition('_')
    if 'DAPI' in chnameprefix:
    #if ch_name == 'DAPI_0'
        ch_index=0
    else:
        if (ch_names.index(ch_name) == 0):
            ch_index = len(ch_names)
        else: 
            ch_index=ch_names.index(ch_name)

    d['ch']=ch_index
    d['ch_name']=ch_name

    #find the index for the imaging sessions
    sess_name=os.path.split(os.path.split(os.path.split(filepath)[0])[0])[1] 
    d['session'] = int(sess_name[sess_name.find("n")+1:])
    #d['session'] = image_sessions.index(sess_name)
    d['session_name']=sess_name

    #get the metafile for this file
    metafile=os.path.splitext(filepath)[0] + '_metadata.txt'
    d['metafile']=metafile


    dl.append(d)
df = pd.DataFrame(dl)

def read_frame_metadata(metafile):
    try:
        f = open(metafile, 'r')
    except IOError:
        print "Could not open meta-data file: %s" %metafile
        return None
    metadata = f.readlines()
    d = {}
    #print metafile
    (channel, width, height, mosaic_x, mosaic_y, scale_x, scale_y, exposure) = metadata[1].split()
    d['width']=int(width)
    d['height']=int(height)
    d['mosaic_x']=int(mosaic_x)
    d['mosaic_y']=int(mosaic_y)
    d['scale_x']=float(scale_x)
    d['scale_y']=float(scale_y)
    d['exposure']=float(exposure)
    (xstage,ystage,zstage)=map(float,metadata[3].split())
    d['xstage']=xstage
    d['ystage']=ystage
    d['zstage']=zstage
    f.close()
    return d

unique_stitches = df.groupby(['ch','section','ribbon','session','zstack'])


for ind,stitch in unique_stitches:
    
    #(metadata,norm_coords)=convertmetadata.get_freeframe_pix_coords(stitch['metafile'].tolist())
    for index,row in stitch.iterrows():

        d=read_frame_metadata(row['metafile'])
        [df.set_value(index,k,d[k]) for k in d.keys()]
  
        #stitch['xstage']=xstage
        #break
    stitch=df.loc[stitch.index]
    df.loc[stitch.index,'a02']=(stitch['xstage']-np.min(stitch['xstage']))/np.min(stitch['scale_x'])
    df.loc[stitch.index,'a12']=(stitch['ystage']-np.min(stitch['ystage']))/np.min(stitch['scale_y'])
    #stitch=df.loc[stitch.index]
    #print stitch
    #break

  
df['a00']=1.0
df['a01']=0.0
df['a10']=0.0
df['a11']=1.0
df['tileID']= df['ch'] + 1000*df['frame'] + 1000*1000*df['section'] + 1000*1000*1000*1000*df['ribbon'] + 1000*1000*1000*1000*100*df['session']+1000*1000*1000*1000*1000*100*df['zstack']
#fixed bug with separating session and zstack numbers

#df = df[df['zstack'] == 0]
ribbons = df.groupby('ribbon')
zoffset = 0

for ribbnum, ribbon in ribbons:
	ribbon.loc[ribbon.index, 'z'] = ribbon['section'] + zoffset
        # print ribbon['section'].max()
        zoffset += ribbon['section'].max() + 1

        df.loc[ribbon.index, 'z'] = ribbon['z'].values

filedir = os.path.dirname(outputfile)
if not os.path.exists(filedir):
	os.makedirs(filedir)
	
df.to_csv(outputfile,index=False)
