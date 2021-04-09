import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for item in self.crossword.variables:
            for domain in self.domains[item].copy():
                if len(domain) != item.length:
                    self.domains[item].remove(domain)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        i, j = self.crossword.overlaps[x, y]

        revised = False

        for word_x in self.domains[x].copy():
            arc_consistent = False
            for word_y in self.domains[y]:
                if word_x[i] == word_y[j]:
                    arc_consistent = True
                    break

            if (not(arc_consistent)):
                self.domains[x].remove(word_x)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Create initial queue 
        if arcs is None:
            arcs = list()
            for variable in self.crossword.variables:
                for neighbor in self.crossword.neighbors(variable):
                    # print((variable, neighbor))
                    arcs.append((variable, neighbor))

        while arcs:
            x, y = arcs.pop()
            revised = self.revise(x, y)

            # Return False when no solution can be found
            if not self.domains[x]:
                return False

            # re-add neighbors to the list
            if revised:
                for neighbor in self.crossword.neighbors(x):
                    arcs.append((x, neighbor))

        # Return True when all arcs are consistent and no domain is empty
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        consistent = True

        used_words = set()

        for var in assignment:
            # Every word can only be used once
            if assignment[var] in used_words:
                consistent = False
                break

            used_words.add(assignment[var])

            # Check unary constraints
            if len(assignment[var]) != var.length:
                consistent = False
                break

            #Check binary constraints
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if assignment[var][i] != assignment[neighbor][j]:
                        consistent = False
                        break

        return consistent

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Create an empty dict
        possible_words = dict()

        # Loop through each word in var's domain and assign a start value of 0
        for word in self.domains[var]:
            possible_words[word] = 0

        # Loop through each neighbor
        
        for neighbor in self.crossword.neighbors(var):
            # continue when  that neighbor already has been assigned
            if neighbor in assignment:
                continue

            for word_x in possible_words:
                for word_y in self.domains[neighbor]:

                    i, j = self.crossword.overlaps[var, neighbor]
                    # When chars are not equal the word would be ruled out
                    if word_x[i] != word_y[j]:
                        possible_words[word_x] += 1

        # Order dict by value
        """
        Key is a function that's called on each element before the values 
        are compared for sorting. The get() method on dictionary objects returns 
        the value of for a dictionary's key.
        """
        sorted_domains = sorted(possible_words, key=possible_words.get)

        return sorted_domains

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        best_choice = None

        for variable in self.crossword.variables:
            if variable in assignment:
                continue

            if not best_choice:
                best_choice = variable
                continue

            # If variable has fewer values in it domain as the current best choice update it
            if len(self.domains[variable]) < len(self.domains[best_choice]):
                best_choice = variable
                continue

            # If the amount of values is the same check the degree
            if len(self.domains[variable]) == len(self.domains[best_choice]):

                # If the degree of variable is bigger than from best choice, update it
                if len(self.crossword.neighbors(variable)) > len(self.crossword.neighbors(best_choice)):
                    best_choice = variable

                # When the degrees are equal leave best_choice unchanged

        return best_choice

    def maintain_arc_consitency(self, assignment, var):
        inferences = dict()

        for neighbor in self.crossword.neighbors(var):
            if neighbor in assignment:
                continue
            
            i, j = self.crossword.overlaps[var, neighbor]

            for word in self.domains[neighbor].copy():
                if word[j] != assignment[var][i]:   
                    self.domains[neighbor].remove(word)
            
            # Add neighbors from the neighbor to a queue to run arc3 on that
            queue = []
            for neighbor2 in self.crossword.neighbors(neighbor):
                queue.append((neighbor, neighbor2))
            
            self.ac3(queue)

        if len(inferences) != 0:
            return inferences
            
        return None


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # Code according to the sudo code from the slides

        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            assignment[var] = value

            if self.consistent(assignment):
                inferences = self.maintain_arc_consitency(assignment, var)
                
                if inferences is not None:
                    for inference in inferences:
                        assignment[inference] = infereces[inference]

                result = self.backtrack(assignment)
                if result is not None:
                    return result
                else: # Remove variables again
                    assignment.pop(var)
                    for inference in inferences:
                        assignment.pop(inference)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
