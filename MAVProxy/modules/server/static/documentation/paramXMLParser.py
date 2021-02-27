from xml.dom import minidom
xmldoc = minidom.parse('apm.xml')
itemlist = xmldoc.getElementsByTagName('param')

with open('apm.js', 'w') as f:
  f.write('var params = [\n')
  for s in itemlist:
    f.write("{name: '")
    f.write(s.attributes['name'].value.replace("ArduPlane:","").replace("'","").replace('"',''))
    param_name = s.attributes['name'].value.replace("ArduPlane:","").replace("'","").replace('"','')
    f.write("', key: '")
    f.write(s.attributes['name'].value.replace("ArduPlane:","").replace("'","").replace('"',''))
    f.write("', description: '")
    try:
      f.write(s.attributes['humanName'].value.replace("'","").replace('"',''))
    except:
      f.write('')
    f.write("', value: '")
    f.write("', user: '")
    try: f.write(s.attributes['user'].value.replace("'","").replace('"',''))
    except: pass
    try:
      for p in s.getElementsByTagName('field'):
        try:
          f.write("', ")
          f.write(str(p.attributes['name'].value).lower())
          f.write(": '")
          f.write(str(p.childNodes[0].data).lower())
        except: pass
    except: pass
    try:
      s.getElementsByTagName('value')
      st = "{"
      for p in s.getElementsByTagName('value'):
        try: 
          st += ("'" + str(p.attributes['code'].value + "'") + ": '" + str(p.childNodes[0].data.replace("'","").replace('"','')) +  "', ")
        except: pass
      st = st[:-2] + "}"
      if len(st) > 1 and param_name != "ARMING_CHECK": f.write("', values: "+ st)
      else: f.write("'")
    except: pass
    f.write(", documentation: '")
    f.write(s.attributes['documentation'].value.replace("'","").replace('"',''))
    f.write("'},\n")
  f.write("];\n")
  f.write("module.exports = params;")
  f.close();