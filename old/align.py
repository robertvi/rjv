

'''
alignment results: use first token as one letter code defining which
fields are present

align(query,subject,fname=None)

query/subject can be db key or list of seqids
fname None => return results from function

sequence(seqid,start,end) => sequence
header(seqid) => header
seqrecord(seqid,start,end) => seqid, header, sequence

'''

