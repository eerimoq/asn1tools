import asn1tools


def main():
  #compile a specification with 2 modules inside
  spec = asn1tools.compile_file('tests/files/Spec.asn', 'uper')
  
  #encode with types from two different modules specified in the same file Spec.asn
  enc_1 = spec.encode('aSequence',{'priority:'High', 'src':1,'dst':2,'num':0,'length':256})
  enc_2 = spec.encode('Seq_Mod_2',{'isvalide':True, 'name':'toto', 'ID':5)

  print(enc_1)
  print(enc_2)


  #decode
  dec_1 = spec.decode('aSequence',enc_1)
  dec_2 = spec.decode('Seq_Mod_2',enc_2)

  print(dec_1)
  print(dec_2)






