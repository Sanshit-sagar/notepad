#ifndef DICTIONARY_TRIE_H
#define DICTIONARY_TRIE_H

#include <vector>
#include <string>
#include <unordered_map>

class Node
{
public:
  Node();
  std::vector<Node*> vector;
  int freqNode;
  bool endWord; 
  ~Node();
};

class DictionaryTrie {
public:
  std::unordered_map<char,int> Number;
  std::unordered_map<int,char> Character;
  Node* root;
  
  DictionaryTrie();
  bool insert(std::string word, unsigned int freq);
  bool find(std::string word) const;
  bool checkValid(std::string word) const; 
  std::vector<std::string> predictCompletions(std::string prefix, unsigned int num_completions);
  Node* insertHelp(std::string word, Node* currNode);  
  ~DictionaryTrie();

private:
  void deleteNodes(Node*);
};

class ComparePriority {
  public:
    bool operator() (std::pair<Node*,std::string>&left, std::pair<Node*,std::string>&right) const {
      return (left.first) ->freqNode < (right.first)->freqNode;
    }     
};

#endif 