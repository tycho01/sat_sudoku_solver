import random
from collections import Counter, defaultdict

class Variable():

    def __init__(self, variable):
        self.variable = variable
        self.flips = 0

    def __repr__(self):
        return 'VAR POINTER: ' + str(self.variable)

class Clause():

    def __init__(self, clause):
        self.clause = clause

class Solver():

    def __init__(self, strategy, clauses, variables):
        self.strategy = strategy
        self.variables_min = variables | set(map(lambda x: -1*x, variables))
        self.variables = {v: Variable(v) for v in self.variables_min}

        self.dict = defaultdict(set)
        self.clauses = self.create_clauses(clauses, variables)
        self.splits = 0
        self.assignments = []

    def create_clauses(self, clauses, variables):
        new_clauses = set()
        for c in clauses:
            var_pointer_clause = set()
            for i in c:
                v = self.variables[i]
                var_pointer_clause.add(v)
            clause = Clause(var_pointer_clause)
            for v in clause.clause:
                self.dict[v].add(clause)
            new_clauses.add(clause)
        return new_clauses

    def solve(self):
        solution = self.backtracking(self.clauses, self.assignments)
        return solution

    def jeroslaw_wang(self, clauses):
        counter = Counter()
        for clause in clauses:
            for literal in clause:
                counter[literal] += 2**len(clause)
        m = counter.most_common(1)[0]
        return m[0]

    def get_counter(self, clauses):
        counter = {}
        for clause in clauses:
            for literal in clause.clause:
                if literal in counter:
                    counter[literal] += 1
                else:
                    counter[literal] = 1
        return counter

    def variable_selection(self, clauses):
        counter = self.get_counter(clauses)
        return random.choice(list(counter))

    def bcp(self, clauses, unit):
        modified = set()
        for clause in clauses:
            if unit in clause.clause: continue
            neg_unit = self.variables[-unit.variable]
            if neg_unit in clause.clause:
                c = Clause([x for x in clause.clause if x != neg_unit])
                if len(c.clause) == 0: return -1
                modified.add(c)
            else:
                modified.add(clause)
        return modified

    def pure_literal(self, clauses):
        counter = self.get_counter(clauses)
        pure_literals = []
        for literal, times in counter.items():
            neg_literal = self.variables[-literal.variable]
            if neg_literal not in counter:
                pure_literals.append(literal)
        for pure in pure_literals:
            clauses = self.bcp(clauses, pure)
        return clauses, pure_literals

    def unit_literal(self, clauses):
        unit_literals = []
        unit_clauses = [c.clause for c in clauses if len(c.clause) == 1]
        while len(unit_clauses) > 0:
            unit = list(unit_clauses[0])[0]
            clauses = self.bcp(clauses, unit)
            unit_literals.append(unit)
            if clauses == -1:
                return -1, []
            if not clauses:
                return clauses, unit_literals
            unit_clauses = [c.clause for c in clauses if len(c.clause) == 1]
        return clauses, unit_literals

    def backtracking(self, clauses, assignments):
        clauses, pure_assignment = self.pure_literal(clauses)
        clauses, unit_assignment = self.unit_literal(clauses)
        assignments = assignments + pure_assignment + unit_assignment

        if clauses == -1:
            return []
        if not clauses:
            return assignments

        if self.strategy == 2:
            variable = self.jeroslaw_wang(clauses)
        else:
            variable = self.variable_selection(clauses)

        variable.flips += 1
        neg_var = self.variables[-variable.variable]
        self.splits += 1
        solution = self.backtracking(self.bcp(clauses, neg_var), assignments + [neg_var])
        if not solution:
            solution = self.backtracking(self.bcp(clauses, variable), assignments + [variable])
        return solution



