from collections import namedtuple

# these constants should be used to indicate the match status of a pair
MATCH = "match"
NON_MATCH = "non-match"
MAYBE_MATCH = "maybe"

# these constants should be used to indicate the similarity of a pair
SIMILARITY_HIGH = "high"
SIMILARITY_MEDIUM = "medium"
SIMILARITY_LOW = "low"


# A named tuple is a tuple with named fields.
# This allows us to access the fields by name instead of by index
# which is more readable and self-documenting.

# Cleaned data is a 4-tuple of id, name, city, and zip
CleanedData = namedtuple("CleanedData", ["id", "org_name", "city", "zip"])

# Similarity is a 3-tuple of name similarity, city similarity, and zip match
SimilarityTuple = namedtuple("Similarity", ["name_sim", "city_sim", "zip_match"])