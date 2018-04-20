import unittest
from final_proj import *



class TestDataSource(unittest.TestCase):

    def test_data_source(self):
        lst = []
        results = get_theaters("theaters livingston nj 07039")
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0], ' AMC DINE-IN Essex Green 9')
        self.assertEqual(results[2], ' Bow Tie South Orange 5')

        for r in results:
            movies = get_movies_for_theater(r)
        self.assertTrue(len(movies) > 0)
        self.assertTrue(type(movies) == list)
        self.assertIn('I Feel Pretty', movies)

class TestDatabase(unittest.TestCase):
    # Test Database after database is populated already

    def test_data(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        statement = '''
        SELECT Id, Name
        FROM Movies
        '''
        cur.execute(statement)

        ids = []
        names = []
        for row in cur:
            id = row[0]
            ids.append(row[0])
            name = row[1]
            names.append(row[1])
        self.assertEqual(names[0], 'Rampage')
        self.assertTrue(ids[0], 1)

    def test_rating(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        statement = '''
        SELECT MPAARating, Id
        FROM Movies
        '''
        cur.execute(statement)

        mpaas = []
        for row in cur:
            mpaa = row[0]
            mpaas.append(mpaa)
        self.assertIn("PG", mpaas)
        self.assertIn("R", mpaas)
        self.assertIn("PG-13", mpaas)

class TestProcessing(unittest.TestCase):
    def test_runtime(self):

        results = runtime_comparison()
        self.assertIn(86, results)
        self.assertTrue(len(results) > 5)
        self.assertTrue(type(results) == list)

    def test_mpaa(self):
        results = mpaa_comparison()
        self.assertIn('PG-13', results)
        self.assertTrue(len(results) > 0)
        self.assertTrue(type(results) == list)

unittest.main()
