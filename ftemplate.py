#!/usr/bin/python

'''
fill out a template file
save as a new file
call qsub on the file
'''

import inspect,os,re,time,random,subprocess

qsub_log_dir = '/home/vicker/qsub_logs'

def next_sample(fname):
	'''
	get next non commented sample name
	skip blank lines
	'''
	
	f = open(fname)
	
	for line in f:
		if line == '': break
		line = line.strip()
		if line.find('#') != -1:
			line = line[:line.index('#')].strip()
		if line == '': continue
		
		yield line
	
	f.close()

def myqsub(inp,out=None,dic=None,sge=True):
    '''
    inp - template file
    out - output file
    dic - key:value dictionary

    replace @{key} with value for all placeholders in the input file
    write to output file
    run qsub

    if dic == None, get key value pairs from name space of calling function

    sge == True => fix commented shell variables that confuse sun grid engine

    out == None => automatically generate a name, in tmp/ if it exists
    '''

    #get local variables from calling function
    if dic == None: dic = get_locals(inspect.currentframe().f_back.f_locals)

    #create random name for output file
    if out == None:
        out = 'tmp/' + str(random.random())[-6:] + '.' + ('%.9f'%time.time()).split('.')[1] + '.sge'
        if not os.path.exists('tmp'): os.makedirs('tmp')

    #fill out the template file, save to new file	
    ftemplate(inp,out,dic,sge)

    #call qsub on the new file
    #capture qsub output to a file
    #output should contain the jobnumber
    os.system('qsub '+out+' | tee '+out+'.qsub')

    #get job number from the file
    f = open(out+'.qsub')
    data = f.read()
    f.close()
    jobnumber = int(data.strip().split()[2])

    #store a copy of the script file to a global log directory
    #rename the script file to be the job number
    os.system('cp '+out+' '+qsub_log_dir+'/%d.sge'%jobnumber)

def ftemplate(inp,out,dic=None,sge=True):
	'''
	inp - template file
	out - output file
	dic - key:value dictionary
	
	replace @{key} with value for all placeholders in the input file
	write to output file
	
	if dic == None, get key value pairs from name space of calling function
	
	sge == True => fix commented shell variables that confuse sun grid engine
	'''

	#get local variables from calling function
	if dic == None: dic = get_locals(inspect.currentframe().f_back.f_locals)
		
	#read template, fill out place holders
	f = open(inp)
	data = sub_templates(f.read(),dic,sge)
	f.close()

	#write out final file
	fout = open(out,'wb')
	fout.write(data)
	fout.close()

def get_locals(tvar):
	'''
	extract only simple local variables from the frame
	'''

	dic = {}
	allowed = [str,int,float,bool]
	
	for k,v in tvar.iteritems():
		if type(k) != str: continue
		if not type(v) in allowed: continue 
		dic[k] = v
		
	del tvar
	return dic

def sub_templates(data,dic,sge=False):
	'''
	substitute values for place holders
	'''
	
	#replace @{key} with value
	for key in dic.iterkeys():
		if not '@{%s}'%key in data: continue
		data = data.replace('@{%s}'%key, str(dic[key]))

	#check all placeholders were replaced
	if '@{' in data:
		for m in re.finditer('@{.*}',data):
			print m.group(0), 'not matched'
		raise Exception
	
	#stop commented shell variables from looking like
	#sun grid engine parameters
	if sge == True: data = data.replace('#${','# ${')
	
	return data

def T(data,dic=None):
	'''
	fill out a template string
	replaces @{key} with value
	must replace all placeholders
	not all keys need be present in the template
	non string keys are ignored
	'''
	
	if dic == None:
		#get local variables from calling function
		dic = get_locals(inspect.currentframe().f_back.f_locals)
	
	return sub_templates(data,dic)

def run(cmd,dic=None):
    '''
    fill out a template string
    run as shell command then return stdout and stderr
    replaces @{key} with value
    must replace all placeholders
    not all keys need be present in the template
    non string keys are ignored
    '''

    if dic == None:
        #get local variables from calling function
        dic = get_locals(inspect.currentframe().f_back.f_locals)

    cmd = sub_templates(cmd,dic)
    return subprocess.check_output(cmd,shell=True)

def myqsub2(inp,out,dic=None,sge=True,bintype=None,arrayjobs=0,mem=1.0,rt=2,name='myjob',ops=None):
	'''
	like qsub but automatically generates the SGE boiler plate
	
	inp - template file
	out - output file
	dic - key:value dictionary
	
	replace @{key} with value for all placeholders in the input file
	write to output file
	run qsub
	
	if dic == None, get key value pairs from name space of calling function
	
	sge == True => fix commented shell variables that confuse sun grid engine
	
	automatically generate the SGE boiler plate options
	bintype guessed from extension of inp file, or set manually eg '/usr/bin/perl'
	arrayjobs = number of array jobs
	mem is gigabytes
	rt is run time in hours
	ops is list of options, minus the leading #$
	eg ['-pe smp @{threads}']
	'''

	if dic == None:
		#get local variables from calling function
		dic = get_locals(inspect.currentframe().f_back.f_locals)
		
	sge_header = []
		
	if bintype == None:
		#auto detect binary type
		if inp.endswith('.py'):
			sge_header.append('#$ -S /usr/bin/python')
		elif inp.endswith('.sh'):
			sge_header.append('#$ -S /bin/sh')
		else:
			raise Exception
	else:
		sge_header.append('#$ -S '+bintype)
		
	sge_header.append('#$ -N '+name)
	sge_header.append('#$ -cwd')
	sge_header.append('#$ -V')
	
	if arrayjobs == 0:
		sge_header.append('#$ -o ../logs/$JOB_NAME.$JOB_ID.out')
		sge_header.append('#$ -e ../logs/$JOB_NAME.$JOB_ID.err')
	else:
		sge_header.append('#$ -o ../logs/$JOB_NAME.$JOB_ID.$TASK_ID.out')
		sge_header.append('#$ -e ../logs/$JOB_NAME.$JOB_ID.$TASK_ID.err')
		sge_header.append('#$ -t 1:%d'%arrayjobs)
	
	sge_header.append('#$ -l h_vmem=%.1fG'%mem)
	sge_header.append('#$ -l h_rt=%d:00:00'%rt)
	if ops != None:
		for x in ops:
			sge_header.append('#$ '+x)
	
	data = '\n'.join(sge_header) + '\n\n'

	f = open(inp)
	data += f.read()
	f.close()
	
	data = sub_templates(data,dic,sge)
	
	fout = open(out,'wb')
	fout.write(data)
	fout.close()
	
	os.system('qsub %s'%out)
