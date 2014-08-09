%module polypartition
%include "std_list.i"
%{
#include "polypartition.h"
%}
namespace std {
   %template(listpoly) list<TPPLPoly>;
};
%include "polypartition.h"
