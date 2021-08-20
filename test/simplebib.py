alph = 'abcdefghijklmnopqrstuvwxyz'

def bibtexparse(stream):
    i = 0
    mode = 'entry'
    submode = ''
    brace_count = 0
    entrytype = ''
    entrytypes = []

    escaped = False

    while i < len(stream):
        #print('mode:' + str(mode),
        #'submode:' + str(submode),
        #'brace count:' + str(brace_count),
        #'stream:' + str(stream[:i+1]),
        #sep=', ')
        if not escaped:
            if stream[i] == '{':
                brace_count += 1
            elif stream[i] == '}':
                brace_count -= 1
            elif stream[i] == '%': # comment
                i = stream.find('\n', i)
            elif stream[i] == '"': # inferred left/right delimitation
                if brace_count % 2 == 0:
                    brace_count += 1
                else:
                    brace_count -= 1


        if mode == 'entry' and submode == '':
            if brace_count == 1: # end entry string
                mode = 'entry'
                submode = 'key'
                entrytypes.append(entrytype)
                keys = []
                values = []
                key = ''
                value = ''
                ekey = ''
            else:
                entrytype += stream[i]
        elif mode == 'entry' and submode == 'key':
            if stream[i] == ',':
                entrytypes.append((entrytypes.pop(), ekey))
                mode = 'field'
                submode = 'key'
            else:
                ekey += stream[i]
        elif mode == 'field' and submode == 'key':
            if stream[i] == '=':
                submode = 'value'
                #print('key',key)
                keys.append(key)
                key = ''
                # white space handling
                while stream[i+1] in [' ', '\n']:
                    i += 1
                value = ''
                # integer parsing (special case of no delimiter)
                while stream[i+1] in '0123456789':
                    value += stream[i+1]
                    i += 1
                if len(value) > 0:
                    values.append(value)
                    submode = 'key'
            else:
                key += stream[i]

            if brace_count == 0:
                mode = 'entry'
                submode = ''
                etype, ekey = entrytypes.pop()
                entrytypes.append({'entrytype':etype,'entrykey':ekey, 'keys':keys,'values':values})
                entrytype = ''

        elif mode == 'field' and submode == 'value':
            if brace_count == 1: # should be 2, for nesting, when getting values
                submode = 'key'
                value += stream[i]
                values.append(value)
                value = ''
            else:
                value += stream[i]

        if stream[i] == '\\' and not escaped:
            escaped = True
        else:
            escaped = False
        i += 1

    return entrytypes

def sanitize(string):
    return string.replace('\n','').replace('\t','').replace(' ','').replace(',','')

def process2dict(entrytypes):
    d = dict()
    for row in entrytypes:
        etype = sanitize(row['entrytype']).lstrip('@')
        ekey = sanitize(row['entrykey'])
        dkv = dict()
        for i in range(len(row['keys'])):
            dkv[sanitize(row['keys'][i])] = row['values'][i].lstrip('{').rstrip('}').strip('"')
        dkv['entrytype'] = etype
        d[ekey] = dkv
    return d

def parsepages(string):
    return [x.split('--') for x in string.split(',')]

if __name__ == '__main__':
    #sample_bib = "@abc{key, a= {z\n y},\nb ={x\n w},\nc = {123},\n d ={uv}}\n@cde{key2, a={abc},b={\\somemacro}}"
    #sample_bib = '@abc{key,a={a}}@abc{key,b={b},}'
    #sample_bib = '@abc{key,a="a"}@abc{key,b="b",intkey=123,otherkey={a}}'
    sample_bib = '@abc{key,a="a\\{a\\}\\}"}@abc{key,b="b\\"",intkey=123,otherkey={a}}'
    etypes = bibtexparse(sample_bib)
#    print(etypes)

    with open('test.bib', 'r') as _:
        etypes = bibtexparse(_.read())

    d = process2dict(etypes)

    # process cross-references (assume inherit everything unless already have it, e.g., no overriding)
    for k in d:
        d1 = d[k]
        if 'crossref' in d1.keys():
            d2 = d[d1['crossref']]
            for k2 in d2:
                try:
                    d1[k2]
                except KeyError:
                    d1[k2] = d2[k2]

    # bibliography
    citation_entrytype2fmt = dict()
    citation_entrykey2fmt = dict()

    # biggest pain: including \ref and \label to allow LaTeX to construct hyperlinks. this hypermedia can't be emulated otherwise
    # this and backref are significant advantages to using Biblatex.

    def wrap_citation(key, citation):
        label = key + alph[counts[key] - 1]

        try:
            places[key].append(label)
        except KeyError:
            places[key] = [label]

        return '{' + citation + ' \\label{' + key + alph[counts[key] - 1] + '}' + '}'

    def formatter_caselaw_citation(key, entry, opts = None, prev=None, ever=None):
        pre = post = None
        if opts == [[['']]]:
            pages = ''
        elif len(opts) == 1:
            pages = ', ' + ','.join('--'.join(x) for x in opts[0])
        elif len(opts) == 2:
            pre = opts[0]
            pages = ', ' + ','.join('--'.join(x) for x in opts[1])
            

        if prev == key:
            return 'ibid' + pages
            if opts is not None:
                return 'ibid, ' + pages
            else:
                return 'ibid'
        if key in ever:
            fmt = '{plaintiffs} v. {defendants}' + pages
        else:
            fmt = '{plaintiffs} v. {defendants}. {volume}~{reporter}~{reporterpage}' + pages + '. ({venue}, {year}).'
        return fmt.format_map(entry)

    citation_entrykey2fmt['specialentrykey'] = 'special value'
    citation_entrytype2fmt['caselaw'] = formatter_caselaw_citation
    citation_entrytype2fmt['appealcase'] = formatter_caselaw_citation
    citation_entrytype2fmt['externalproceeding'] = formatter_caselaw_citation

    def try_in_order_citation(key, entry, opts=None, prev=None, ever=None):
        try:
            return citation_entrykey2fmt[key](key, entry,opts,prev,ever)
        except KeyError:
            try:
                fmt = citation_entrytype2fmt[entry['entrytype']]
                return fmt(key, entry,opts,prev,ever)
            except KeyError:
                return None

    # reading
    with open('ibid-idem.tex', 'r') as _:
        r = _.read()

    i = 0
    prev = None
    ever = set()
    counts = dict()
    pagecum = dict()
    places = dict()

    print('making citations (to be in-line substituted)')
    print()
    while r.find('\\cite', i) > 0:
        i = r.find('\\cite', i)
        j1 = r.find('{', i)
        j2 = r.find('}', j1)
        opts = r[i+5:j1]
        opts = [x.strip('[').strip(']') for x in opts.split('][')]
        key = r[j1+1:j2]

        if len(opts) == 1:
            l = parsepages(opts[0])
            opts[0] = l
            try:
                pagecum[key].append(l)
            except KeyError:
                pagecum[key] = [l]

        elif len(opts) == 2:
            l = parsepages(opts[1])
            opts[1] = l
            try:
                pagecum[key].append(l)
            except KeyError:
                pagecum[key] = [l]

        citation = try_in_order_citation(key, d[key], opts, prev, ever)
        # process citation here

        i = j2
        prev = key
        ever.add(key)
        try:
            counts[key] += 1
        except KeyError:
            counts[key] = 1

        print(wrap_citation(key, citation))
    print()

    # bibliography
    # verbose style, keep the same entry type
#    entrytype2fmt = dict()
#    entrykey2fmt = dict()
    from collections import defaultdict
    supremacy = defaultdict()
    supremacy.default_factory = 10 
    #cits = sorted(ever, key=lambda x:(counts[x],supremacy[d[x]['venue']], d[x]['plaintiffs']))
    cits = sorted(ever, key=lambda x:-counts[x]) #,supremacy[d[x]['venue']], d[x]['plaintiffs']))

    def formatter_caselaw_bib(key, entry):
        pages = pagecum[key]
        #pages = compress pages into page range (hard to do with section and other numbering mixed in)
        pages = ', ' + ','.join('--'.join(x[0]) for x in sorted(pages)) # need to concatenate
        backrefs = 'see ' + ','.join('\\ref{' + x + '}' for x in places[key])

        fmt = '{plaintiffs} v. {defendants}. {volume}~{reporter}~{reporterpage}' + pages + '. ({venue}, {year}).'

        return fmt.format_map(entry) + backrefs

    bib_entrytype2fmt = dict()
    bib_entrykey2fmt = dict()

    bib_entrytype2fmt['caselaw'] = formatter_caselaw_bib
    bib_entrytype2fmt['appealcase'] = formatter_caselaw_bib
    bib_entrytype2fmt['externalproceeding'] = formatter_caselaw_bib
    bib = ''

    def try_in_order_bib(key, entry):
        try:
            return bib_entrykey2fmt[key](key, entry,opts,prev,ever)
        except KeyError:
            try:
                fmt = bib_entrytype2fmt[entry['entrytype']]
                return fmt(key, entry)
            except KeyError:
                return None

    print('making bibliography to be placed at end')
    print()
    for key in cits:
        entry = d[key]
        bibentry = try_in_order_bib(key, d[key])
        print(bibentry)
