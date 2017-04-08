#include <algorithm>
#include <cmath>
#include <cstring>
#include <fstream>
#include <sstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>
#include <map>
#include <boost/dynamic_bitset.hpp>
#include <boost/program_options.hpp>

namespace po = boost::program_options;

using namespace std;
using namespace boost;

class Corpus {
public:
    string text;
    dynamic_bitset<> utt_boundaries;
    dynamic_bitset<> boundaries;
    map<char, double> p_phonemes;

    Corpus(string path)
    {
        load_file({path});
        compute_p_phonemes();
    }

    Corpus(string path, string trained_path,
           dynamic_bitset<> &trained_boundaries)
    {
        load_file({path, trained_path});
        compute_p_phonemes();

        // set the trained boundaries as unchangable utterance boundaries
        trained_boundaries.resize(text.size() + 1, false);
        utt_boundaries |= trained_boundaries;
    }

    double p0(string word, double p_hash=0.5)
    {
        double p = 1;
        for (char ph : word)
            p *= p_phonemes[ph];

        return p_hash * pow(1 - p_hash, word.size() - 1) * p;
    }

    vector<string> get_words()
    {
        vector<string> words;
        dynamic_bitset<> bounds = utt_boundaries | boundaries;

        for (int i = 0; i < text.size(); ++i) {
            if (bounds[i])
                words.push_back(string());

            words.back().append(1, text[i]);
        }

        return words;
    }

private:
    virtual void load_file(const vector<string> &paths)
    {
        string line;
        stringstream text_stream;
        vector<int> utt_indices = {0};

        for (string path : paths) {
            fstream in(path);

            while (getline(in, line)) {
                text_stream << line;
                utt_indices.push_back(utt_indices.back() + line.size());
            }

            in.close();
        }


        text = text_stream.str();

        utt_boundaries = dynamic_bitset<>(text.size() + 1);
        boundaries = dynamic_bitset<>(text.size() + 1);

        for (int index : utt_indices) {
            utt_boundaries[index] = 1;
        }
    }

    void compute_p_phonemes()
    {
        for (char phoneme : text) {
            // only compute if the char isn't in the map yet
            if (p_phonemes.find(phoneme) == p_phonemes.end())
                p_phonemes[phoneme] = count(text.begin(), text.end(), phoneme) /
                    (double)text.size();
        }
    }
};

map<string, int> histogram(const vector<string> &vec)
{
    map<string, int> counts;
    vector<string> unique_words;

    unique_copy(vec.begin(), vec.end(), back_inserter(unique_words));

    for (const string &word : unique_words) {
        if (counts.find(word) == counts.end())
            counts[word] = 1;
        else
            counts[word] += 1;
    }

    return counts;
}

void find_enclosing_boundaries(dynamic_bitset<> bounds, int i,
                               int *lower, int *upper)
{
    *lower = i - 1;
    while (!bounds[*lower])
        *lower -= 1;

    *upper = i + 1;
    while (!bounds[*upper])
        *upper += 1;
}

void gibbs_iteration(Corpus &corpus, double rho=2.0, double alpha=0.5,
                     double p_hash=0.5)
{
    dynamic_bitset<> bounds = corpus.utt_boundaries | corpus.boundaries;
    vector<string> words = corpus.get_words();
    map<string, int> word_counts = histogram(words);

    for (int i = 0; i < corpus.text.size(); ++i) {
        char phoneme = corpus.text[i];

        if (corpus.utt_boundaries[i])
            continue;

        int lower, upper;
        find_enclosing_boundaries(bounds, i, &lower, &upper);

        string w1 = corpus.text.substr(lower, (upper - lower));
        string w2 = corpus.text.substr(lower, (i - lower));
        string w3 = corpus.text.substr(i, (upper - i));

        double n_;
        if (!bounds[i])
            n_ = words.size();
        else
            n_ = words.size() - 1;

        double n_dollar = corpus.utt_boundaries.count() - 1;
        double nu = corpus.utt_boundaries[upper] ? n_dollar : n_ - n_dollar;

        double p_h1_factor1;
        if (!bounds[i])
            p_h1_factor1 = (word_counts[w1] - 1 + alpha * corpus.p0(w1, p_hash)) / (n_ + alpha);
        else
            p_h1_factor1 = (word_counts[w1] + alpha * corpus.p0(w1, p_hash)) / (n_ + alpha);

        double p_h1_factor2 = (nu + rho/2) / (n_ + rho);

        double p_h2_factor1, p_h2_factor3;
        if (!bounds[i]) {
            p_h2_factor1 = (word_counts[w2] + alpha * corpus.p0(w2, p_hash)) / (n_ + alpha);
            p_h2_factor3 = ((word_counts[w3] + (w2 == w3 ? 1 : 0) + alpha *
                             corpus.p0(w3, p_hash)) / (n_ + 1 + alpha));
        } else {
            p_h2_factor1 = (word_counts[w2] - 1 + alpha * corpus.p0(w2, p_hash)) / (n_ + alpha);
            p_h2_factor3 = ((word_counts[w3] - 1 + (w2 == w3 ? 1 : 0) + alpha *
                             corpus.p0(w3, p_hash)) / (n_ + 1 + alpha));
        }

        double p_h2_factor2 = (n_ - n_dollar + rho/2) / (n_ + rho);
        double p_h2_factor4 = ((nu + (w2 == w3 ? 1 : 0) + rho/2) / (n_ + 1 + rho));

        double p_h1 = p_h1_factor1 * p_h1_factor2;
        double p_h2 = p_h2_factor1 * p_h2_factor2 * p_h2_factor3 * p_h2_factor4;

        if (p_h2 > p_h1)
            corpus.boundaries[i] = 1;
        else
            corpus.boundaries[i] = 0;
    }
}

void write_boundaries(const Corpus &corpus, string filename)
{
    ofstream out(filename);
    out << "[";

    for (int i = 0; i < corpus.text.size(); ++i) {
        if (i != 0)
            out << ", ";
        out << corpus.boundaries[i];
    }

    out << "]";
    out.close();
}

dynamic_bitset<> read_boundaries(string path)
{
    fstream in(path);
    string line;
    getline(in, line);
    in.close();

    auto end_iter = remove_if(line.begin(), line.end(),
                              [](char ch) {return !(ch == '1' || ch == '0');});
    line.erase(end_iter, line.end());

    return dynamic_bitset<>(line);
}

string generate_filepath(const string &out_dir, double alpha, double p_hash, int i=-1)
{
    stringstream s;
    s << out_dir << "/";
    if (i >= 0)
        s << "iter_" << i << "_";
    s << alpha << "_" << p_hash << ".txt";

    return s.str();
}

int main(int argc, char *argv[])
{
    string out_dir;
    string train_path;
    string test_path;
    string boundaries;
    double alpha;
    double p_hash;
    vector<int> eval_points;

    po::options_description desc("Usage");
    desc.add_options()
        ("alpha,a", po::value<double>(&alpha)->default_value(0.5), "alpha parameter")
        ("p_hash,ph", po::value<double>(&p_hash)->default_value(0.5), "p# parameter")
        ("out_dir", po::value<string>(&out_dir), "path to write output to")
        ("train_path", po::value<string>(&train_path), "path to load training data")
        ("test_path", po::value<string>(&test_path), "path to load test data")
        ("test", "apply a learned model to test data (requires test_path and boundaries)")
        ("help", "print usage information")
        ("boundaries", po::value<string>(&boundaries), "path to a learned set of boundaries")
        (",n", po::value<vector<int> >(&eval_points)->multitoken(), "points to evaluate");

    po::variables_map opts;
    po::store(po::parse_command_line(argc, argv, desc), opts);
    po::notify(opts);

    if (opts.count("help")) {
        cout << desc << endl;
        return 0;
    }

    string out_path = generate_filepath(out_dir, alpha, p_hash);

    Corpus *corpus;
    if (opts.count("test")) {
        cout << "Testing" << endl;
        auto bounds = read_boundaries(boundaries);
        corpus = new Corpus(train_path, test_path, bounds);
    } else {
        corpus = new Corpus(train_path);
    }

    // calculate the maximum iteration
    int i_max = *max_element(eval_points.begin(), eval_points.end());

    for (int i = 0; i < i_max; ++i) {
        cout << "Iteration " << i << endl;
        gibbs_iteration(*corpus, 2, alpha, p_hash);

        if (find(eval_points.begin(), eval_points.end(), i) != eval_points.end()) {
            string iterpath = generate_filepath(out_dir, alpha, p_hash, i);
            write_boundaries(*corpus, iterpath);
        }
    }

    write_boundaries(*corpus, out_path);

    return 0;
}
