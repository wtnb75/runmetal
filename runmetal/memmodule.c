#include <Python.h>

static PyObject *mem_peek(PyObject *self, PyObject *args){
  unsigned long a1, a2;
  unsigned long *val;
  if (!PyArg_ParseTuple(args, "ll", &a1, &a2)){
    return NULL;
  }
  val=(unsigned long *)(a1+a2);
  return PyLong_FromUnsignedLong(*val);
}

static PyObject *mem_copy(PyObject *self, PyObject *args){
  unsigned long a1;
  int a2;
  char *val;
  if (!PyArg_ParseTuple(args, "li", &a1, &a2)){
    return NULL;
  }
  val=(char *)a1;
  return Py_BuildValue("y#", val, a2);
}

static PyObject *mem_put(PyObject *self, PyObject *args){
  unsigned long a1;
  const char *a2;
  int a3;
  if (!PyArg_ParseTuple(args, "s#l", &a2, &a3, &a1)){
    return NULL;
  }
  void *p=(void *)a1;
  // printf("%#lx %#lx %#lx\n", a1, (long)a2, (long)a3);
  memcpy(p, a2, a3);
  return PyLong_FromLong(a3);
}

static PyObject *mem_dput(PyObject *self, PyObject *args){
  unsigned long a1;
  const char *a2;
  int a3;
  if (!PyArg_ParseTuple(args, "lil", &a2, &a3, &a1)){
    return NULL;
  }
  void *p=(void *)a1;
  // printf("%#lx %#lx %#lx\n", a1, (long)a2, (long)a3);
  memcpy(p, a2, a3);
  return PyLong_FromLong(a3);
}

static PyMethodDef MemMethods[]={
  {"peek", mem_peek, METH_VARARGS, "peek memory"},
  {"copy", mem_copy, METH_VARARGS, "copy memory"},
  {"put", mem_put, METH_VARARGS, "put to memory"},
  {"dput", mem_dput, METH_VARARGS, "direct put to memory"},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef memmodule ={
  PyModuleDef_HEAD_INIT,
  "mem",
  NULL,
  -1,
  MemMethods
};

PyMODINIT_FUNC
PyInit_mem(void){
  return PyModule_Create(&memmodule);
}
