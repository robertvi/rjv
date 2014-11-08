def next_hit(f):
    '''
    return the next blast hit from a tab separated outfmt 6 file
    '''
    
    flag = False
    if type(f) == str:
        f = open(f)
        flag = True

    for line in f:
        tok = line.strip().split('\t')
        hit = {}
        hit['query'] = tok[0]
        hit['subject'] = tok[1]
        hit['pident'] = float(tok[2])
        hit['alen'] = int(tok[3])
        hit['mismatch'] = int(tok[4])
        hit['gaps'] = int(tok[5])
        hit['qstart'] = int(tok[6])
        hit['qend'] = int(tok[7])
        hit['sstart'] = int(tok[8])
        hit['send'] = int(tok[9])
        hit['evalue'] = float(tok[10])
        hit['bscore'] = float(tok[11])

        yield hit
        
    if flag: f.close()
