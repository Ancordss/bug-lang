%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "token.h"
#include <stdbool.h>

#include <iostream>
#include <fstream>
#include <vector>
#include <cstdio>

char* tokens_estadosattributes[100];// Tamaño suficiente para tokens de estados
int num_tokens_estadosattributes = 0;
char* tokens_iniciales[100]; // Tamaño suficiente para tokens de iniciales
int num_tokens_iniciales = 0;
char* tokens_finalesattributes[100]; // Tamaño suficiente para tokens de finalesattributes
int num_tokens_finalesattributes = 0;
char *tokens_transicionales[100]; // Tamaño suficiente para tokens de estados transicionales
int num_tokens_transicionales = 0; 
char* tokens_linearlayout[100]; // Tamaño suficiente para tokens de linearlayout
int num_tokens_linearlayout = 0; 
FILE *vitacora_errores_file = NULL;

/** Extern from Flex **/
extern int lineno, 
           line_init;

extern char str_buf[256];    
extern char* str_buf_ptr;
extern FILE *yyin;


/*Flex and bison*/
  extern int yylex();
  extern char *yytext;
  extern FILE *yyin;
  

  extern void yyterminate();

/* Variables for error handling and saving */
int error_count=0; 
int flag_err_type=0; // 0: Token Error (YYTEXT) || 1: String Error (STRBUF)
int scope=0;
int pos_number=0;
int flag=0;  //flag gia to token ean einai swsto to android
int valueflag=0;
char* strint;



// vars james
char* t_alfabeto0; // Variable para el primer T_STRING
char* t_alfabeto1; // Variable para el segundo T_STRING
int found_match = 0; // Bandera para indicar si se encontró una coincidencia


/*Specific Functions*/
void yyerror(const char *message);
%}

%define parse.error verbose

%union{
   int intval;
   float floatval;
   char charval;
   char *strval;
}


/*Keywords*/
%token<strval> T_AUTOMATA_AFN
%token<strval> T_ALFABETO
%token<strval> T_ESTADO
%token<strval> T_INICIAL
%token<strval> T_FINAL
%token<strval> T_TRANSICIONES
%token<strval> T_END_TAG
%token<strval> T_INT
%token<strval> T_ALPHANUM

%token<strval> T_END_ALFABETO
%token<strval> T_END_AUTOMATA_AFN
%token<strval> T_END_ESTADO
%token<strval> T_END_INICIAL
%token<strval> T_END_FINAL
%token<strval> T_END_TRANSICIONES

%token<strval> T_SIMBOLO

%token<strval> T_COMMENT_OPEN
%token<strval> T_COMMENT_CLOSE

%token<strval> T_STRING
%token<strval> T_STRING_SINGLE_QUOTE
%token<strval> T_POSITIVE_INTEGER
%token<strval> T_SLASH_END_TAG
%token<strval> T_STRING_DQ_SPACE


/*Other tokens*/
%left  <strval> T_DOT                      "."
%left  <strval> T_COMMA                    ","
%right <strval> T_ASSIGN                   "="
%token <strval> T_COLON                    ":"
%left  <strval> T_LBRACK                   "["
%left  <strval> T_RBRACK                   "]"
%token <strval> T_SLASH                    "/"
%token <strval> T_EXCLAMATION              "!"
%token <strval> T_DASH                     "-"
%token <strval> T_LBRACES                  "{"
%token <strval> T_RBRACES                  "}"
%left  <strval> T_AT                       "@"
%token <strval> T_QUESTION_MARK            "?"
%token <strval> T_UNDERSCORE               "_"
%token <strval> T_HASH                     "#"
%token <strval> T_SQUOTES                  "'"

/*EOF*/
%token <strval> T_EOF          0           "end of file"

/*Non-Terminal*/
%type  program linearlayout linearlayoutattributes        
%type  estados estadosattributes                                                                                    
%type  text content contentempty element         
                                                        
                                                                                  
%type <strval> letra_a letra_b 


%start program

%%

/*Grammar Rules*/

program :                 T_AUTOMATA_AFN linearlayout estados iniciales finales transicionales T_END_AUTOMATA_AFN
                        | linearlayout estados iniciales finales transicionales
                        ;

// linearlayout:              T_LINEAR_LAYOUT linearlayoutattributes element T_END_LINEAR_LAYOUT
//                         |  T_LINEAR_LAYOUT linearlayoutattributes element  T_END_LINEAR_LAYOUT linearlayout
//                         ;

linearlayout: T_ALFABETO alfabeto_letras  T_END_ALFABETO;


                              
                        
alfabeto_letras: T_STRING T_STRING {
        t_alfabeto0 = strdup($1); // Almacena el valor del primer T_STRING en t_alfabeto0
        t_alfabeto1 = strdup($2); // Almacena el valor del segundo T_STRING en t_alfabeto1
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($1);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($2);
    }
    |   T_STRING T_STRING T_STRING{
        t_alfabeto0 = strdup($1); // Almacena el valor del primer T_STRING en t_alfabeto0
        t_alfabeto1 = strdup($2); // Almacena el valor del segundo T_STRING en t_alfabeto1
        t_alfabeto1 = strdup($3); // Almacena el valor del segundo T_STRING en t_alfabeto2
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($1);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($2);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($3);
    }
    |   T_STRING T_STRING T_STRING T_STRING{
        t_alfabeto0 = strdup($1); // Almacena el valor del primer T_STRING en t_alfabeto0
        t_alfabeto1 = strdup($2); // Almacena el valor del segundo T_STRING en t_alfabeto1
        t_alfabeto1 = strdup($3); // Almacena el valor del segundo T_STRING en t_alfabeto2
        t_alfabeto1 = strdup($4); // Almacena el valor del segundo T_STRING en t_alfabeto3
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($1);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($2);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($3);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($4);
    }
    |   T_STRING T_STRING T_STRING T_STRING T_STRING{
        t_alfabeto0 = strdup($1); // Almacena el valor del primer T_STRING en t_alfabeto0
        t_alfabeto1 = strdup($2); // Almacena el valor del segundo T_STRING en t_alfabeto1
        t_alfabeto1 = strdup($3); // Almacena el valor del segundo T_STRING en t_alfabeto2
        t_alfabeto1 = strdup($4); // Almacena el valor del segundo T_STRING en t_alfabeto3
        t_alfabeto1 = strdup($5); // Almacena el valor del segundo T_STRING en t_alfabeto4
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($1);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($2);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($3);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($4);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($5);
    }
    |   T_STRING T_STRING T_STRING T_STRING T_STRING T_STRING{
        t_alfabeto0 = strdup($1); // Almacena el valor del primer T_STRING en t_alfabeto0
        t_alfabeto1 = strdup($2); // Almacena el valor del segundo T_STRING en t_alfabeto1
        t_alfabeto1 = strdup($3); // Almacena el valor del segundo T_STRING en t_alfabeto2
        t_alfabeto1 = strdup($4); // Almacena el valor del segundo T_STRING en t_alfabeto3
        t_alfabeto1 = strdup($5); // Almacena el valor del segundo T_STRING en t_alfabeto4
        t_alfabeto1 = strdup($6); // Almacena el valor del segundo T_STRING en t_alfabeto5
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($1);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($2);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($3);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($4);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($5);
        tokens_linearlayout[num_tokens_linearlayout++] = strdup($6);
    }


simbolos: T_SIMBOLO
                
                
estados:                 T_ESTADO  estadosattributes T_END_ESTADO  
                        ;
                   
estadosattributes: T_INT T_INT {
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($1);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($2);
        }
        | T_INT T_INT T_INT T_INT {
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($1);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($2);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($3);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($4);
        }
        | T_INT T_INT T_INT {
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($1);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($2);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($3);
        }
        | T_INT T_INT T_INT T_INT T_INT {
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($1);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($2);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($3);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($4);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($5);
        }
        | T_INT T_INT T_INT T_INT T_INT T_INT{
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($1);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($2);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($3);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($4);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($5);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($6);
        }
        | T_INT T_INT T_INT T_INT T_INT T_INT T_INT{
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($1);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($2);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($3);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($4);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($5);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($6);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($7);
        }
        | T_INT T_INT T_INT T_INT T_INT T_INT T_INT T_INT{
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($1);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($2);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($3);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($4);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($5);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($6);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($7);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($8);
        }
        | T_INT T_INT T_INT T_INT T_INT T_INT T_INT T_INT T_INT{
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($1);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($2);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($3);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($4);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($5);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($6);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($7);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($8);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($9);
        }
        | T_INT T_INT T_INT T_INT T_INT T_INT T_INT T_INT T_INT T_INT{
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($1);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($2);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($3);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($4);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($5);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($6);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($7);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($8);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($9);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($10);
        }
        | T_INT T_INT T_INT T_INT T_INT T_INT T_INT T_INT T_INT T_INT T_INT{
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($1);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($2);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($3);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($4);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($5);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($6);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($7);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($8);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($9);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($10);
            tokens_estadosattributes[num_tokens_estadosattributes++] = strdup($11);
        }                        
;


iniciales:          T_INICIAL T_INT T_END_INICIAL {
                    tokens_iniciales[num_tokens_iniciales++] = strdup($2);
                }
                ;


finales:                 T_FINAL finalesattributes T_END_FINAL
                        ;


finalesattributes: T_INT {
                    tokens_finalesattributes[num_tokens_finalesattributes++] = strdup($1);
                }
                | T_INT T_INT {
                    tokens_finalesattributes[num_tokens_finalesattributes++] = strdup($1);
                    tokens_finalesattributes[num_tokens_finalesattributes++] = strdup($2);
                }
                ;


transicionales:         T_TRANSICIONES transicionalesattributes T_END_TRANSICIONES
                        ;


transicionalesattributes: T_INT T_COMMA  T_STRING  T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($1), $3, atoi($5));

                            int error_line = lineno;

                             if (strcmp($3, t_alfabeto0) != 0 && strcmp($3, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $3);
                                    yyerror(error_message);
                                }
                            
                            tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                            //printf("Transicionales %s\n", tokens_transicionales[0]);

                         }
                          
                         T_INT T_COMMA T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($7), $9, atoi($11));

                            tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }


                         T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($13), $15, atoi($17));

                             int error_line = lineno;

                             if (strcmp($15, t_alfabeto0) != 0 && strcmp($15, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $14);
                                    yyerror(error_message);
                                }

                            tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }
                          
                         T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($19), $21, atoi($23));

                             int error_line = lineno;

                             if (strcmp($21, t_alfabeto0) != 0 && strcmp($21, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $20);
                                    yyerror(error_message);
                                }
                                tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }
                          
                         T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($25), $27, atoi($29));

                             int error_line = lineno;

                             if (strcmp($27, t_alfabeto0) != 0 && strcmp($27, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $26);
                                    yyerror(error_message);
                                }
                                tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }
                        
                         T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($31), $33, atoi($35));

                             int error_line = lineno;

                             if (strcmp($33, t_alfabeto0) != 0 && strcmp($33, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $32);
                                    yyerror(error_message);
                                }
                                tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }

                         T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($37), $39, atoi($41));

                             int error_line = lineno;

                             if (strcmp($39, t_alfabeto0) != 0 && strcmp($39, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $38);
                                    yyerror(error_message);
                                }
                                tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }

                        T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($43), $45, atoi($47));

                             int error_line = lineno;

                             if (strcmp($45, t_alfabeto0) != 0 && strcmp($45, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $44);
                                    yyerror(error_message);
                                }
                                tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }

                         T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($49), $51, atoi($53));

                             int error_line = lineno;

                             if (strcmp($51, t_alfabeto0) != 0 && strcmp($51, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $50);
                                    yyerror(error_message);
                                }
                                tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }

                         T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($55), $57, atoi($59));

                             int error_line = lineno;

                             if (strcmp($57, t_alfabeto0) != 0 && strcmp($57, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $56);
                                    yyerror(error_message);
                                }
                                tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }

                         T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($61), $63, atoi($65));

                             int error_line = lineno;

                             if (strcmp($63, t_alfabeto0) != 0 && strcmp($63, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $62);
                                    yyerror(error_message);
                                }
                                tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }

                        T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($67), $69, atoi($71));

                             int error_line = lineno;

                             if (strcmp($69, t_alfabeto0) != 0 && strcmp($69, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $68);
                                    yyerror(error_message);
                                }
                                tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }

                        T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($73), $75, atoi($77));

                             int error_line = lineno;

                             if (strcmp($75, t_alfabeto0) != 0 && strcmp($75, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $74);
                                    yyerror(error_message);
                                }
                                tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }

                         T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($79), $81, atoi($83));

                             int error_line = lineno;

                             if (strcmp($81, t_alfabeto0) != 0 && strcmp($81, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $80);
                                    yyerror(error_message);
                                }
                                tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }

                        T_INT T_COMMA  T_STRING T_COMMA  T_INT
                         {
                            char concatenated_values[100]; // Crear un buffer para almacenar la cadena concatenada
                            sprintf(concatenated_values, "%d,%s,%d", atoi($85), $87, atoi($89));

                             int error_line = lineno;

                             if (strcmp($87, t_alfabeto0) != 0 && strcmp($87, t_alfabeto1) != 0)
                                {
                                    char error_message[100];
                                    sprintf(error_message, "One CHARACTER at line %d does not match values %s or %s that were entered in ALFABETO found %s ", error_line, t_alfabeto0, t_alfabeto1, $86);
                                    yyerror(error_message);
                                }
                                tokens_transicionales[num_tokens_transicionales++] = strdup(concatenated_values);
                         }

                         ;
                          


                             
comment:                 T_COMMENT_OPEN T_STRING T_COMMENT_CLOSE
                          ;


content:                  element
                        | element content
                        ;

contentempty:            element
                        | element content
                        | %empty
                        ;

element:                  estados element
                        | iniciales element
                        | finales element             
                        |%empty
                        ;               
                       



%%



void cleanup_parser() {
    memset(tokens_estadosattributes, 0, sizeof(tokens_estadosattributes));
    num_tokens_estadosattributes = 0;

    memset(tokens_iniciales, 0, sizeof(tokens_iniciales));
    num_tokens_iniciales = 0;

    memset(tokens_finalesattributes, 0, sizeof(tokens_finalesattributes));
    num_tokens_finalesattributes = 0;

    memset(tokens_transicionales, 0, sizeof(tokens_transicionales));
    num_tokens_transicionales = 0;

    memset(tokens_linearlayout, 0, sizeof(tokens_linearlayout));
    num_tokens_linearlayout = 0;
}

char** get_tokens_linearlayout() {
        return tokens_linearlayout;
    }


char** get_tokens_estadosattributes(){
    return tokens_estadosattributes;
}


char** get_tokens_transcicionales() {
        return tokens_transicionales;
    }

char** get_tokens_finalesattributes() {
    return tokens_finalesattributes;
}

char** get_tokens_iniciales() {
    return tokens_iniciales;
}

void close_vitacora(){

    fflush(vitacora_errores_file);
    fclose(vitacora_errores_file);
    vitacora_errores_file = NULL;
}

int parse_xml() {
    int token;

    yyrestart(yyin);

    // Realiza el análisis sintáctico
    yyparse();

    // Cierra el archivo y realiza cualquier limpieza necesaria
    fclose(yyin);




    if (error_count > 0) {
        printf(" ");

    } else {
        printf("Syntax Analysis completed successfully.\n");

    }
    

    return 0;
}

int main(int argc, char *argv[]) {
    // Esta función principal se mantendrá, pero no será la función principal de la biblioteca
    // if (argc > 1) {
    //     parseXML(argv[1]);
    // }
    // return 0;

    int token;


    if(argc > 1){
        yyin = fopen(argv[1], "r");
        if (yyin == NULL){
            perror ("Error opening file"); 
            return -1;
        }
    }

    init_parser(xml_file_ptr);

    yyrestart(yyin);

    // Realiza el análisis sintáctico
    yyparse();

    // Cierra el archivo y realiza cualquier limpieza necesaria
    fclose(yyin);

    if (error_count > 0) {
        printf(" ");

    } else {
        printf("Syntax Analysis completed successfully.\n");

    }
    

    return 0;

}

// int main(int argc, char *argv[]){
//     int token;

    

    
//     if(argc > 1){
//         yyin = fopen(argv[1], "r");
//         if (yyin == NULL){
//             perror ("Error opening file"); 
//             return -1;
//         }
//     }

    
//     yyparse();


//    if(error_count > 0){
//         printf("Syntax Analysis failed due to %d errors\n", error_count);
//       }
        
//    else{
//         printf("Syntax Analysis completed successfully.\n");
//         //         printf("TOKENS ENCONTRADOS:\n");
//         // int max_tokens = num_tokens_estadosattributes;
//         // if (num_tokens_iniciales > max_tokens) {
//         //     max_tokens = num_tokens_iniciales;
//         // }
//         // if (num_tokens_finalesattributes > max_tokens) {
//         //     max_tokens = num_tokens_finalesattributes;
//         // }
//         // if (num_tokens_transicionales > max_tokens) {
//         //     max_tokens = num_tokens_transicionales;
//         // }

//         // // Imprimir tokens de ALFABETO
//         // for (int i = 0; i < num_tokens_linearlayout; i++) {
//         //     printf("TOKEN FOUND in ALFABETO: %s\n", tokens_linearlayout[i]);
//         // }

//         // // Imprimir tokens de ESTADOS
//         // for (int i = 0; i < num_tokens_estadosattributes; i++) {
//         //     printf("TOKEN FOUND in ESTADOS: %d\n", tokens_estadosattributes[i]);
//         // }

//         // // Imprimir tokens de INICIAL
//         // for (int i = 0; i < num_tokens_iniciales; i++) {
//         //     printf("TOKEN FOUND in INICIAL: %d\n", tokens_iniciales[i]);
//         // }

//         // // Imprimir tokens de FINAL
//         // for (int i = 0; i < num_tokens_finalesattributes; i++) {
//         //     printf("TOKEN FOUND in FINAL: %d\n", tokens_finalesattributes[i]);
//         // }

//         // // Imprimir tokens de TRANSICIONALES
//         //  for (int i = 0; i < num_tokens_transicionales; i++) {
//         //         printf("TOKEN FOUND in TRANSICIONALES tokens_transicionales[%d] = %s\n", i, tokens_transicionales[i]);
//         //  }

        
//       }

//     return 0;
//     yyrestart(yyin);
//     fclose(yyin);
// }


// void yyerror(const char *message)
// {
//     error_count++;
    
//     if(flag_err_type==0){
//         printf("-> ERROR at line %d caused by %s : %s\n", lineno,  message);
//     }else if(flag_err_type==1){
//         *str_buf_ptr = '\0'; 
//         printf("-> ERROR at line %d near \"%s\": %s\n", lineno, str_buf, message);
//     }

//     flag_err_type = 0; 
//     if(MAX_ERRORS <= 0) return;
//     if(error_count == MAX_ERRORS){
//         printf("Max errors (%d) detected. ABORTING...\n", MAX_ERRORS);
//         exit(-1);
//     }
// }

void init_vitacora_error_file(){

    if (vitacora_errores_file == NULL) { 
        vitacora_errores_file = fopen("vitacora_errores.html", "a");
        if (vitacora_errores_file == NULL) {
            perror("Error al abrir el archivo vitacora_errores.html");
            exit(-1);
        }
        
        // Escribe el encabezado HTML y el estilo básico en el archivo.
        fprintf(vitacora_errores_file, "<!DOCTYPE html>\n<html>\n<head>\n");
        fprintf(vitacora_errores_file, "<style>\n");
        fprintf(vitacora_errores_file, "  body { font-family: Arial, sans-serif; background-color: #f5f5f5; }\n");
        fprintf(vitacora_errores_file, "  .container { max-width: 800px; margin: 0 auto; padding: 20px; background-color: #fff; box-shadow: 0 0 5px rgba(0, 0, 0, 0.2); }\n");
        fprintf(vitacora_errores_file, "  h1 { text-align: center; }\n");
        fprintf(vitacora_errores_file, "  .error { color: red; font-weight: bold; }\n");
        fprintf(vitacora_errores_file, "</style>\n");
        fprintf(vitacora_errores_file, "</head>\n<body>\n");
        fprintf(vitacora_errores_file, "<div class='container'>\n");
        fprintf(vitacora_errores_file, "<h1>Error Log</h1>\n");
    }

}

void yyerror(const char *message) {
    error_count++;
    
    // Abre el archivo en modo de escritura (creándolo si no existe).
    init_vitacora_error_file();

    // Escribe el error en el archivo HTML.
    fprintf(vitacora_errores_file, "<p class='error'>ERROR at line %d: %s</p>\n", lineno, message);
    printf("ERROR at line %d: %s\n", lineno, message);

    if (MAX_ERRORS > 0 && error_count >= MAX_ERRORS) {
        fprintf(vitacora_errores_file, "<p class='error'>Max errors (%d) detected. ABORTING...</p>\n", MAX_ERRORS);
        printf("Max errors (%d) detected. ABORTING...\n", MAX_ERRORS);
        fclose(vitacora_errores_file); // Cierra el archivo HTML
        exit(-1);
    }
}
