CXX = clang++
CXXFLAGS = -std=c++17 -O2 -Wall -MMD -MP -IGeneticAlgorithm

# all GA sources except the app entry point
LIB_SRC = $(filter-out GeneticAlgorithm/main.cpp, $(wildcard GeneticAlgorithm/*.cpp))
LIB_OBJ = $(LIB_SRC:.cpp=.o)

all: tsp

tsp: $(LIB_OBJ) GeneticAlgorithm/main.o
	$(CXX) $(CXXFLAGS) -o $@ $^

tsp_tests: $(LIB_OBJ) tests/tests.o
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

test: tsp_tests
	./tsp_tests

clean:
	rm -f GeneticAlgorithm/*.o GeneticAlgorithm/*.d tests/*.o tests/*.d tsp tsp_tests

# --- Python visualization (auto-uses a project-local virtualenv; no manual activation) ---
VENV_PY = .venv/bin/python3

# create the venv and install deps on first use
$(VENV_PY):
	python3 -m venv .venv
	.venv/bin/python3 -m pip install -q --upgrade pip
	.venv/bin/python3 -m pip install -q -r requirements.txt

# live animated dashboard (run ./tsp solve first to generate results/)
viz: $(VENV_PY)
	$(VENV_PY) visualize.py

# Roulette vs Tournament figure (run ./tsp experiment first)
compare: $(VENV_PY)
	$(VENV_PY) compare_selection.py

.PHONY: all test clean viz compare

# Auto-generated header dependencies: editing a header rebuilds every object that
# includes it (prevents silently linking stale objects as later tasks edit headers).
-include $(LIB_OBJ:.o=.d) GeneticAlgorithm/main.d tests/tests.d
