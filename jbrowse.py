import os

def show_blast_hits(hits,query=False,pause=False):
    '''
    launch one firefox tab for each subject (or query) id
    add additional jbrowse track showing where the blast hits are
    firefox should already be running when this is called
    
    query == True means query is the reference sequence
    query == False means subject is the reference sequence
    
    #blast+ hits outfmt 6, tab separated values
    #0qseqid 1sseqid 2pident 3length 4mismatch 5gapopen 6qstart 7qend 8sstart 9send 10evalue 11bitscore
    #load using:
    hits = [x for x in csv.reader(open(fname),delimiter='\t')]
    
    see:
    http://gmod.org/wiki/JBrowse_Configuration_Guide#Controlling_JBrowse_with_the_URL_Query_String
    '''

    grouped = {}

    #group hits by subject id (or query id)
    for hit in hits:
        if query:
            uid = hit[0] #qseqid
        else:
            uid = hit[1] #sseqid

        if not uid in grouped: grouped[uid] = []
        
        grouped[uid].append(hit)

    #[{ "seq_id":"ctgA", "start": 123, "end": 456, "name": "MyBLASTHit"},...}]
    for uid in grouped.iterkeys():
        #list of features to display on this scaffold
        feature_list = []
        for hit in grouped[uid]:
            if query:
                name = hit[1] #sseqid
                start = int(hit[6])
                end = int(hit[7])
            else:
                name = hit[0] #qseqid
                start = int(hit[8])
                end = int(hit[9])
                
            #ensure start <= end
            if start > end: start,end = end,start
            
            feature_list.append('{"seq_id":"%s","start":%d,"end":%d,"name":"%s"}'%(uid,start,end,name))
            
        url = 'http://localhost/jbrowse/?loc=%s:1..9999999'%uid
        url += '&addFeatures=[' + ','.join(feature_list) + ']'
        url += '&addTracks=[{"label":"blast","store":"url","type":"JBrowse/View/Track/HTMLFeatures"}]'
        url += '&tracks=HIGH,LOW,augMaz,augOat,PASA,exOat,exTran,exUni,RM,TPSI,NNN,blast'
        
        #print url
        
        os.system("firefox '%s'"%url)#url string must be protected from bash using single quotes
        
        if pause == True:
            raw_input('press enter...')
