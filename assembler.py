import argparse, re

def twosComplement(bits, value):
  """
    Represent a decimal value in 2s complement
  """
  if value < 0:
    value = (1 << bits) + value
  formatstring = '{:0%ib}' % bits
  return formatstring.format(value)

def compToBinary(comp):
  """
    Converts the 'comp' field of a C-instruction to binary
  """
  if comp == '0':
    return '0101010'
  elif comp == '1':
    return '0111111'
  elif comp == '-1':
    return '0111010'
  elif comp == 'D':
    return '0001100'
  elif comp == 'A':
    return '0110000'
  elif comp == '!D':
    return '0001101'
  elif comp == '!A':
    return '0110001'
  elif comp == '-D':
    return '0001111'
  elif comp == '-A':
    return '0110011'
  elif comp == 'D+1':
    return '0011111'
  elif comp == 'A+1':
    return '0110111'
  elif comp == 'D-1':
    return '0001110'
  elif comp == 'A-1':
    return '0110010'
  elif comp == 'D+A':
    return '0000010'
  elif comp == 'D-A':
    return '0010011'
  elif comp == 'A-D':
    return '0000111'
  elif comp == 'D&A':
    return '0000000'
  elif comp == 'D|A':
    return '0010101'
  elif comp == 'M':
    return '1110000'
  elif comp == '!M':
    return '1110001'
  elif comp == '-M':
    return '1110011'
  elif comp == 'M+1':
    return '1110111'
  elif comp == 'M-1':
    return '1110010'
  elif comp == 'D+M':
    return '1000010'
  elif comp == 'D-M':
    return '1010011'
  elif comp == 'M-D':
    return '1000111'
  elif comp == 'D&M':
    return '1000000'
  elif comp == 'D|M':
    return '1010101';

def destToBinary(dest):
  """
    Converts the 'dest' field of a C-instruction to binary
  """
  if not dest:
    return '000'
  elif dest == 'M':
    return '001'
  elif dest == 'D':
    return '010'
  elif dest == 'MD':
    return '011'
  elif dest == 'A':
    return '100'
  elif dest == 'AM':
    return '101'
  elif dest == 'AD':
    return '110'
  elif dest == 'AMD':
    return '111'

def jumpToBinary(jump):
  """
    Converts the 'jump' field of a C-instruction to binary
  """
  if not jump:
    return '000'
  elif jump == 'JGT':
    return '001'
  elif jump == 'JEQ':
    return '010'
  elif jump == 'JGE':
    return '011'
  elif jump == 'JLT':
    return '100'
  elif jump == 'JNE':
    return '101'
  elif jump == 'JLE':
    return '110'
  elif jump == 'JMP':
    return '111'

predefinedSymbols = {
  'SP': 0,
  'LCL': 1,
  'ARG': 2,
  'THIS': 3,
  'THAT': 4,
  'SCREEN': 16384,
  'KBD': 24576
}

# Open the specified file given as an argument
parser = argparse.ArgumentParser()
parser.add_argument('filename', help = 'name of the assembly file', type = str)
args = parser.parse_args()
filename = args.filename

# Read the content of the specified file
result = ''
fname = filename.replace('.asm', '')
with open(filename) as f:
  s = f.read()

  # Remove withspace, comments and empty lines
  s = re.sub('\/\/.*', '', s)
  s = re.sub('\n\n', '', s)
  s = [x.strip() for x in s.split('\n') if x]

  # First pass: build the symbol table
  symbolTable = dict()
  n = 0
  for line in s:
    # Check if current line is a label
    match = re.search('\(.*\)', line)
    if match:
      labelName = match.group().replace('(', '').replace(')', '')
      symbolTable[labelName] = n
    else:
      n += 1
  
  # Second pass: translate to binary
  ROMAddr = 16
  for line in s:
    match = re.search('@.*', line)

    # Handle A-instructions: check if the address is a symbol or a literal number
    if match:
      address = match.group().replace('@', '')
      registerMatch = re.search('R\d+', line)
     
      if registerMatch:
        # Address is a register (R0-R15)
        R = int(registerMatch.group().replace('R', ''))
        result += '0' + twosComplement(15, R) + '\n'
      elif address in predefinedSymbols:
        # Address is a predefined symbol
        result += '0' + twosComplement(15, predefinedSymbols[address]) + '\n'
      elif address.isdigit():
        # Address is a literal number
        result += '0' + twosComplement(15, int(address)) + '\n'
      elif address in symbolTable:
        # Already in symbol table
        result += '0' + twosComplement(15, symbolTable[address]) + '\n'
      else:
        # It's a variable: store it in the next RAM location
        result += '0' + twosComplement(15, ROMAddr) + '\n'
        symbolTable[address] = ROMAddr
        ROMAddr += 1 
    # Handle C-instructions: dest=comp;jump
    # either dest or jump can be left off
    else:
      if '=' in line and ';' not in line:
        # dest=comp
        dest = line.split('=')[0] 
        comp = line.split('=')[1]
        result += '111' + compToBinary(comp) + destToBinary(dest) + '000\n'
      elif '=' in line and ';' in line:
        # dest=comp;jump
        dest = line.split('=')[0] 
        comp = line.split('=')[1].split(';')[0]
        jump = line.split(';')[1]
        result += '111' + compToBinary(comp) + destToBinary(dest) + jumpToBinary(jump) + '\n'
      elif '=' not in line and ';' in line:
        # comp;jump
        dest = False
        comp = line.split(';')[0]
        jump = line.split(';')[1]
        result += '111' + compToBinary(comp) + destToBinary(dest) + jumpToBinary(jump) + '\n'

  # Write object code to a file with the same name as the input file
  f = open(fname + '.hack', 'w')
  f.write(result)
  f.close()
