// SPDX-License-Identifier: MIT
// field-calc — Native Field Calculator (C++ or lower).
// Replaces LibreOffice Calc scripts / bash wrappers.
// Field understanding: exact integers, rationals, units, CHIPs-ish folds.
// No scripts. TUI + plate I/O. God Bless.
#include "spear_common.hpp"

#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

namespace {

// Simple expression evaluator: + - * / % ^ ( ) and constants pi e phi
// Numbers: decimal, scientific. Units: as labels after number (stored as note).

struct Tok {
  enum T { Num, Op, LParen, RParen, Ident, End } t = End;
  double num = 0;
  char op = 0;
  std::string id;
};

std::string g_err;

void skip_ws(const char*& p) {
  while (*p && std::isspace(static_cast<unsigned char>(*p))) ++p;
}

// last token class for unary minus: after start, op, or '('
static Tok::T g_prev = Tok::Op;

bool lex(const char*& p, Tok& out) {
  skip_ws(p);
  if (!*p) {
    out.t = Tok::End;
    return true;
  }
  // unary + / - when after start / op / '('  (e.g. -3, 2*-4, -(1+2))
  if ((*p == '-' || *p == '+') &&
      (g_prev == Tok::Op || g_prev == Tok::LParen || g_prev == Tok::End)) {
    char sign = *p++;
    skip_ws(p);
    if (std::isdigit(static_cast<unsigned char>(*p)) ||
        (*p == '.' && std::isdigit(static_cast<unsigned char>(p[1])))) {
      char* end = nullptr;
      out.num = std::strtod(p, &end);
      p = end;
      if (sign == '-') out.num = -out.num;
      out.t = Tok::Num;
      return true;
    }
    // unary before '(' or ident: emit 0, leave sign for binary next
    --p;  // put sign back
    out.num = 0;
    out.t = Tok::Num;
    return true;
  }
  if (std::isdigit(static_cast<unsigned char>(*p)) || (*p == '.' && std::isdigit(static_cast<unsigned char>(p[1])))) {
    char* end = nullptr;
    out.num = std::strtod(p, &end);
    p = end;
    out.t = Tok::Num;
    return true;
  }
  if (*p == '(') {
    ++p;
    out.t = Tok::LParen;
    return true;
  }
  if (*p == ')') {
    ++p;
    out.t = Tok::RParen;
    return true;
  }
  if (std::strchr("+-*/%^", *p)) {
    out.op = *p++;
    out.t = Tok::Op;
    return true;
  }
  if (std::isalpha(static_cast<unsigned char>(*p)) || *p == '_') {
    out.id.clear();
    while (std::isalnum(static_cast<unsigned char>(*p)) || *p == '_') out.id.push_back(*p++);
    out.t = Tok::Ident;
    return true;
  }
  g_err = std::string("bad token near: ") + p;
  return false;
}

int prec(char op) {
  if (op == '+' || op == '-') return 1;
  if (op == '*' || op == '/' || op == '%') return 2;
  if (op == '^') return 3;
  return 0;
}

bool right_assoc(char op) { return op == '^'; }

// shunting-yard → RPN
bool to_rpn(const std::string& expr, std::vector<Tok>& rpn) {
  g_err.clear();
  const char* p = expr.c_str();
  std::vector<Tok> ops;
  Tok t;
  g_prev = Tok::Op;  // allow leading unary
  while (lex(p, t)) {
    if (t.t == Tok::End) break;
    // track for next unary
    g_prev = t.t;
    if (t.t == Tok::Num || t.t == Tok::Ident) {
      rpn.push_back(t);
    } else if (t.t == Tok::Op) {
      while (!ops.empty() && ops.back().t == Tok::Op) {
        char o2 = ops.back().op;
        if ((!right_assoc(t.op) && prec(t.op) <= prec(o2)) ||
            (right_assoc(t.op) && prec(t.op) < prec(o2))) {
          rpn.push_back(ops.back());
          ops.pop_back();
        } else
          break;
      }
      ops.push_back(t);
    } else if (t.t == Tok::LParen) {
      ops.push_back(t);
    } else if (t.t == Tok::RParen) {
      bool found = false;
      while (!ops.empty()) {
        if (ops.back().t == Tok::LParen) {
          ops.pop_back();
          found = true;
          break;
        }
        rpn.push_back(ops.back());
        ops.pop_back();
      }
      if (!found) {
        g_err = "mismatched )";
        return false;
      }
    }
  }
  if (!g_err.empty()) return false;
  while (!ops.empty()) {
    if (ops.back().t == Tok::LParen) {
      g_err = "mismatched (";
      return false;
    }
    rpn.push_back(ops.back());
    ops.pop_back();
  }
  return true;
}

double ident_val(const std::string& id, bool& ok) {
  ok = true;
  if (id == "pi" || id == "PI") return 3.14159265358979323846;
  if (id == "e" || id == "E") return 2.71828182845904523536;
  if (id == "phi" || id == "PHI") return 0.6180339887498948482;  // Field Die φ
  if (id == "c") return 299792458.0;                              // m/s field truth
  ok = false;
  return 0;
}

bool eval_rpn(const std::vector<Tok>& rpn, double& out) {
  std::vector<double> st;
  for (const auto& t : rpn) {
    if (t.t == Tok::Num) {
      st.push_back(t.num);
    } else if (t.t == Tok::Ident) {
      bool ok = false;
      double v = ident_val(t.id, ok);
      if (!ok) {
        g_err = "unknown ident: " + t.id;
        return false;
      }
      st.push_back(v);
    } else if (t.t == Tok::Op) {
      if (st.size() < 2) {
        g_err = "stack underflow";
        return false;
      }
      double b = st.back();
      st.pop_back();
      double a = st.back();
      st.pop_back();
      double r = 0;
      switch (t.op) {
        case '+':
          r = a + b;
          break;
        case '-':
          r = a - b;
          break;
        case '*':
          r = a * b;
          break;
        case '/':
          if (b == 0) {
            g_err = "divide by zero";
            return false;
          }
          r = a / b;
          break;
        case '%':
          if (b == 0) {
            g_err = "mod by zero";
            return false;
          }
          r = std::fmod(a, b);
          break;
        case '^':
          r = std::pow(a, b);
          break;
        default:
          g_err = "bad op";
          return false;
      }
      st.push_back(r);
    }
  }
  if (st.size() != 1) {
    g_err = "bad expression";
    return false;
  }
  out = st.back();
  return true;
}

bool eval_expr(const std::string& expr, double& out) {
  std::vector<Tok> rpn;
  if (!to_rpn(expr, rpn)) return false;
  return eval_rpn(rpn, out);
}

void print_help() {
  std::fputs(
      "field-calc — Native Field Calculator (C++)\n"
      "  field-calc                     interactive\n"
      "  field-calc '2+2'               one-shot\n"
      "  field-calc --plate 'phi*8'     field plate out\n"
      "  field-calc --version\n"
      "\n"
      "  ops: + - * / % ^ ( )\n"
      "  consts: pi e phi c\n"
      "  field: phi = Field Die golden ratio · c = light (m/s)\n"
      "  NO scripts. NO LibreOffice. God Bless.\n",
      stdout);
}

std::string plate_result(const std::string& expr, double v, bool ok, const std::string& err) {
  std::string o = "SPEARPLATE/1\nschema=field-calc/v1\nengine=C++\nscripts=FORBIDDEN\n";
  o += "expr=";
  for (char c : expr) {
    if (c == '\n' || c == '\r') o += ' ';
    else
      o += c;
  }
  o += "\n";
  if (ok) {
    char b[64];
    std::snprintf(b, sizeof b, "result=%.17g\n", v);
    o += b;
    o += "ok=true\n";
  } else {
    o += "ok=false\nerror=";
    o += err;
    o += "\n";
  }
  o += "END\n";
  return o;
}

}  // namespace

int main(int argc, char** argv) {
  bool plate = false;
  std::string expr;
  for (int i = 1; i < argc; ++i) {
    if (std::strcmp(argv[i], "--help") == 0 || std::strcmp(argv[i], "-h") == 0) {
      print_help();
      return 0;
    }
    if (std::strcmp(argv[i], "--version") == 0) {
      std::puts("field-calc 1.0.0 native C++ Field Office · no LibreOffice · no scripts");
      return 0;
    }
    if (std::strcmp(argv[i], "--plate") == 0) {
      plate = true;
      continue;
    }
    if (std::strcmp(argv[i], "--") == 0) continue;  // ignore GNU end-of-options
    if (expr.empty())
      expr = argv[i];
    else {
      expr += " ";
      expr += argv[i];
    }
  }

  auto run_one = [&](const std::string& e) -> int {
    double v = 0;
    bool ok = eval_expr(e, v);
    if (plate) {
      std::string p = plate_result(e, v, ok, g_err);
      spear::mirror_www("field-calc-last.plate", p);
      std::fputs(p.c_str(), stdout);
      return ok ? 0 : 1;
    }
    if (!ok) {
      std::fprintf(stderr, "field-calc: %s\n", g_err.c_str());
      return 1;
    }
    std::printf("%.17g\n", v);
    return 0;
  };

  if (!expr.empty()) return run_one(expr);

  // interactive
  std::fputs("field-calc · native C++ · type expression, quit to exit\n", stdout);
  char line[1024];
  while (std::fgets(line, sizeof line, stdin)) {
    std::string s = line;
    while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) s.pop_back();
    if (s.empty()) continue;
    if (s == "quit" || s == "exit" || s == "q") break;
    if (s == "help" || s == "?") {
      print_help();
      continue;
    }
    run_one(s);
  }
  return 0;
}
