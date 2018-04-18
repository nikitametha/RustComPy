import ply.lex as lex
import ply.yacc as yacc
import re
from prettytable import PrettyTable

keywords = [ "break", "else", "char",  "return",  "const", "continue", "void",  "if", "static", "while"]
local_names = {}
error_list = []
count = 0
scope = 0
symbol_table = dict()
line_dict = dict()
symbol_table[0] = {}
symbol_table[1] = {}
line_dict[0] = 0

data = []

with open("rust.rs") as file:
	data = file.readlines()
backup = 0
line = 1
b = [0]
for i in data:
	if("{" in i):
		b.append(backup)
		# line_dict[line] = backup
		# line += 1
		scope += 1
		backup = scope
		# continue
	line_dict[line] = backup
	if("}" in i):
		# backup -= 1
		backup = b.pop()
		line_dict[line] = backup
	line += 1

for i in line_dict:
	print (i, " : ", line_dict[i], " : ", data[i-1])

def print_symbol_table():
	global symbol_table
	for i in symbol_table:
		print "\n\n\n\n"
		print "SCOPE ",i
		t = PrettyTable(['Token', 'Line Numbers', 'Type', 'Name', 'Value'])
		for j in symbol_table[i]:
			t.add_row([ j , symbol_table[i][j]['line'], symbol_table[i][j]['type'], symbol_table[i][j]['name'], symbol_table[i][j]['value']])
		print t




tokens = (
    'MAIN', 'PRINT', 'NAME','NUMBER', 'PLUS','MINUS','TIMES','DIVIDE','EQUALS',
    'LPAREN','RPAREN', 'BLOCKSTART', 'BLOCKEND',
    'KEYWORD', 'FLOAT', 'TYPE', 'SEMCOL', 'LE', 'GE', 
    'LT', 'GT', 'EQ', 'NE', 'NEWLINE','ignore',
    'INCREMENT', 'DECREMENT', 'PLEQ', 'MINEQ', 'DIVEQ', 'MULEQ', 
    'SQROPEN', 'SQRCLOSE','AND',
    'OR' ,'BITAND','BITOR','BITNOT','NOT','COL','COMMA','LET','STR'
    )

t_AND     = r'\&\&'
t_OR      = r'\|\|'
t_BITAND  = r'\&'
t_BITOR   = r'\|'
t_BITNOT  = r'\^'
t_NOT     = r'\!'
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_EQUALS  = r'='
t_LPAREN  = r'[(]'
t_RPAREN  = r'[)]'
t_SEMCOL  = r';'
t_INCREMENT = r'\+\+'
t_DECREMENT = r'--'
t_PLEQ = r'\+='
t_MINEQ = r'-='
t_MULEQ = r'\*='
t_DIVEQ = r'/='
t_GT = r'>'
t_GE = r'>='
t_LT = r'<'
t_LE = r'<='
t_EQ = r'=='
t_NE = r'!='
t_COMMA = r','
t_SQROPEN = r'\['
t_SQRCLOSE = r'\]'
t_COL = r':'


def t_PRINT(t):
    r'[p][r][i][n][t][!]'
    global symbol_table
    #print "t.lineno for print",t.lineno
    temp = line_dict[t.lineno - 1]
    #print "line number for print     : ", t.lineno - 1
    if(temp not in symbol_table):
        parent = line_dict[t.lineno - 1 - 1]
        #print "parent : ", parent
        symbol_table[temp] = dict(symbol_table[parent])
    if(t.value not in symbol_table[temp]):
        symbol_table[temp][t.value] = {"name" : "PRINT", "value" : None, "type" : None, "line" : []}
    symbol_table[temp][t.value]["line"].append(count)
    return t


def t_MAIN(t):
    r'[f][n][\ ][m][a][i][n][(][)]'
    global symbol_table
    temp = 0
    #print "main t.value = ", t.value
    if(temp not in symbol_table):
        symbol_table[temp] = dict()
    symbol_table[temp][t.value] = {"name" : "MAIN()", "line" : count, "value": "N/A", "type":"N/A"}
    return t 


def t_CHAR(t):
	r'\'.\'|\'\\n\'|\'\\t\'|\'\\r\'|\'\\b\''
	print("token : ", t)
	return t

def t_LET(t):
	r'[l][e][t]'
	return t

def t_NUMBER(t):
	r'\d+'
	t.value = int(t.value)
	return t

def t_KEYWORD(t):
	r'break|else|return|continue|if|static|while'
	#print("keyword detected")
	global symbol_table
	temp = 0
	if(temp not in symbol_table):
		symbol_table[temp] = dict()
	if(t.value not in symbol_table[temp]):
		symbol_table[temp][t.value] = {"name" : "KEYWORD", "line" : [], "type":"N/A","value":"N/A"}
	symbol_table[temp][t.value]["line"].append(count)
	return t

def t_STR(t):
	r'["].*["]'
	print "string =", t.value

def t_NAME(t):
	r'[a-zA-Z_][a-zA-Z0-9_]*'
	# if(t.value not in keywords):
	#     t.value = str(t.value)
	#     #print("variable name detected : ", t.value)
	global symbol_table
	temp = line_dict[t.lexer.lineno]
	if(temp not in symbol_table):
		parent = line_dict[t.lexer.lineno - 1]
		symbol_table[temp] = dict(symbol_table[parent])
	if(t.value not in symbol_table[temp]):
		symbol_table[temp][t.value] = {"name" : "IDENTIFIER", "value" : None, "type" : None, "line" : []}
	symbol_table[temp][t.value]["line"].append(count)
	return t

def t_BLOCKSTART(t):
	r'\{'
	global symbol_table
	temp = line_dict[t.lexer.lineno]
	if(temp not in symbol_table):
		parent = line_dict[t.lexer.lineno - 1]
		symbol_table[temp] = dict(symbol_table[parent])
	return t


def t_BLOCKEND(t):
	r'\}'
	#print("block ended")
	global scope 
	scope -= 1
	return t

def t_NEWLINE(t):
	r'[\n]+'
	global count
	# print "before : t.lexer.lineno : ", t.lexer.lineno
	t.lexer.lineno += t.value.count("\n")
	# print "after : t.lexer.lineno : ", t.lexer.lineno
	count = t.lexer.lineno
	#print("****line number***" , t.lexer.lineno)
	pass

# Ignored characters
def t_ignore_tab(t):
	r'[\t\ ]'
	pass

def t_ignore_comment(t):
	r'/[*][^*]*[*]+([^/*][^*]*[*]+)*/|//[^\n]*'
	pass

def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lexer = lex.lex()




precedence = (
	('left','PLUS','MINUS'),
	('left','TIMES','DIVIDE'),
	)

def p_main_dec(p):
	'statement : MAIN'
	print("Main parsed!")

def p_print_stat(p):
	'statement : PRINT LPAREN STR RPAREN SEMCOL'
	print "PRINT statement parsed!"	
	

def p_if_statement(p):
	'statement : KEYWORD expression statement'
	if(p[1] != 'if'):
		error_list.append("invalid keyword : " + str(p[1]) + "at line : " + str(count))	
	else:
		print "Parsed a simple if"

def p_if_else_statement(p):
	'statement : KEYWORD expression statement KEYWORD statement'
	if(p[1] != 'if' and p[4]!='else'):
		error_list.append("invalid keyword : " + str(p[1]) + "at line : " + str(count))	
	else:
		print "parsed an if else"

def p_block_declaration(p):
	'statement : BLOCKSTART statement BLOCKEND'
	print("BLOCK END DONE")

def p_multiple_statement(p):
	'statement : statement statement'
	print("multiple statement called")


def p_statement_break_cont(p):
	'statement : KEYWORD'
	if(p[1] != 'break' and p[1] != 'continue'):
		error_list.append("invalid keyword : " + str(p[1]) + "at line : " + str(count))		

def p_statement_declaration_assign(p):
	'statement : LET NAME EQUALS expression SEMCOL'
	print "\n let name equals exp, statement called"
	global count
	global symbol_table
	temp = line_dict[count - 1]
	print(temp)
	print("1", p[1])
	print("2", p[2])
	print("3", p[3])
	print("4", p[4])
	print("type : ", type(p[4]))
	if(p[2] in symbol_table[temp]):
		symbol_table[temp][p[2]]['value'] = p[4]
		symbol_table[temp][p[2]]['type'] = type(p[4])
	else:
		print("else called")
		error_list.append("redefinition of type for variable : " + str(p[2]) + "at line : " + str(count))


def p_statement_dec(p):
	'statement : NAME EQUALS expression SEMCOL'
	print("statement redefinition")
	#CHECK FOR MUT, otherwise error
	print(p[1])


def p_statement_expr2(p):
	'statement : expression SEMCOL'
	print("statement expression2")
	print(p[1])

def p_statement_expr(p):
	'statement : expression'
	print "statement expression "
	print(p[1])

def p_while_exp(p):
	'while_expression : expression'

def p_statement_while(p):
	'statement : KEYWORD while_expression statement'
	if(p[1] != "while"):
		error_list.append("invalid keyword : " + str(p[1]) + "at line : " + str(count))




def p_expression_relop(p):
	'''
	expression : expression GT expression
			   | expression GE expression
			   | expression LT expression
			   | expression LE expression
			   | expression EQ expression
			   | expression NE expression
	'''
	if p[2] == 'GT'  : p[0] = p[1] > p[3]
	elif p[2] == 'GE': p[0] = p[1] >= p[3]
	elif p[2] == 'EQ': p[0] = p[1] == p[3]
	elif p[2] == 'LT': p[0] = p[1] < p[3]
	elif p[2] == 'LE': p[0] = p[1] <= p[3]
	elif p[2] == 'NE': p[0] = p[1] != p[3]

def p_expression_binop(p):
	'''expression : expression PLUS expression 
				  | expression MINUS expression 
				  | expression TIMES expression 
				  | expression DIVIDE expression'''
	if p[2] == '+'  : p[0] = p[1] + p[3]
	elif p[2] == '-': p[0] = p[1] - p[3]
	elif p[2] == '*': p[0] = p[1] * p[3]
	elif p[2] == '/': p[0] = p[1] / p[3]

def p_expression_binop_assign(p):
	'expression : binop_exp'

def p_binop_assign(p):
	'''binop_exp : expression PLEQ expression 
				  | expression MINEQ expression 
				  | expression MULEQ expression 
				  | expression DIVEQ expression'''
	if p[2] == '+'  : p[0] = p[1] + p[3]
	elif p[2] == '-': p[0] = p[1] - p[3]
	elif p[2] == '*': p[0] = p[1] * p[3]
	elif p[2] == '/': p[0] = p[1] / p[3]

def p_increment_first(p):
	'expression : increment_exp'

def p_decrement_first(p):
	'expression : decrement_exp'

def p_decrement(p):
	'decrement_exp : DECREMENT NAME'
	# p[0] = p[2] - 1

def p_increment(p):
	'increment_exp : INCREMENT NAME'
	# p[0] = p[2] + 1

def p_expression_logop(p):
	'''expression : expression AND expression 
				  | expression OR  expression 
				  | expression BITAND expression 
				  | expression BITOR expression
				  | expression BITNOT expression
				  | NOT expression''' 

	if p[2] == 'AND'  : p[0] = p[1] and p[3]
	elif p[2] == 'OR': p[0] = p[1] or p[3]
	elif p[2] == 'BITAND': p[0] = p[1] & p[3]
	elif p[2] == 'BITOR': p[0] = p[1] | p[3] 
	elif p[2] == 'BITNOT': p[0] = p[1] ^ p[3]
	elif p[1] == 'NOT': p[0] = not p[2]

def p_expression_uminus(p):
	'expression : MINUS expression'
	p[0] = -p[2]

def p_expression_group(p):
	'expression : LPAREN expression RPAREN'
	p[0] = p[2]

def p_expression_number(p):
	'expression : NUMBER'
	print "expression=numberr"
	p[0] = p[1]

def p_expression_name(p):
	'expression : NAME'
	print ("p[1] here is", find_val(p[1]))
	p[0] = find_val(p[1])
	

def find_val(x):
	for i in symbol_table:
		if x in symbol_table[i]:
			return symbol_table[i][x]["value"]



def p_error(p):
	if(p != None):
		print count , "Syntax error :" , p 

import ply.yacc as yacc
yacc.yacc()

new_data = "" 
with open("rust.rs") as file:
	new_data = file.read()
i = 0
s = new_data
yacc.parse(s)
print "\n"
print_symbol_table()