import os
import random
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    damping_random = random.random()

    if damping_random <= damping_factor and corpus[page] != '':
        links = list(corpus[page])
        random_link = random.choice(links)
        return random_link
    else:
        random_page = random.choice(list(corpus.keys()))
        return random_page


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    clicks = dict()

    for index in range(n):
        if index == 0:
            page = random.choice(list(corpus.keys()))
            clicks[page] = 1
            continue

        page = transition_model(corpus, page, damping_factor)

        if page in clicks:
            clicks[page] += 1
        else:
            clicks[page] = 1

    prob = dict()
    sum = 0

    for page in clicks:
        prob[page] = clicks[page] / n
        sum += prob[page]

    # print(clicks)
    # print(prob)
    return prob


def NumLinks(corpus, page):
    return len(corpus[page])


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    prob = dict()
    newprob = dict()

    for page in corpus:
        prob[page] = 1 / len(corpus)

    print(prob)

    while True:

        for page in prob:
            total = 0.0

            for possible_page in corpus:
                if page in corpus[possible_page]:
                    total += prob[possible_page] / len(corpus[possible_page])

                if not corpus[possible_page]:
                    total += prob[possible_page] / len(corpus)

            newprob[page] = (1-damping_factor) / \
                len(corpus) + damping_factor * total

            print(newprob[page])

            prob[page] = newprob[page]

            if all(math.isclose(newprob[page], prob[page], abs_tol=0.001) for page in corpus):
                break


if __name__ == "__main__":
    main()
