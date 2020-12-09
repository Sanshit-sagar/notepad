#include "util.h"
#include "DictionaryTrie.h"
#include <unordered_map>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

DictionaryTrie::DictionaryTrie(){
	int minimum = 0; 
	int numLetters =27;     
	root = new Node();    

	for(int i =0; i<numLetters;i++){
		char curr = char(97 + i);
		Number[curr] = i;           
		Character[i] = (int)(curr);  
	}
	Number[' '] = 26;        
	Character[26] = ' ';          
}


Node::Node(){
	int numLetters =27;           
	for(int i =0; i<numLetters; i++){
		vector.push_back(NULL); 
	}
	endWord = false;              
	freqNode = 1;                 
}

bool DictionaryTrie::checkValid(std::string word) const {
for(size_t i=0; i<word.length(); i++) {
if((word[i]!=' ') && (word[i] <'a' || word[i] > 'z')) {
	return false; 
	}
}
return true; 
}

Node* DictionaryTrie::insertHelp(std::string word, Node* currNode) 
{
for(size_t i=0; i<word.length();i++){
		char currWord = (char)word[i];     
		int index = Number[currWord];         
		if(currNode ->vector[index] == NULL){
			currNode->vector[index] = new Node();   
		}
		currNode = currNode->vector[index];      
	}
	return currNode; 
}

bool DictionaryTrie::insert(std::string word, unsigned int freq)
{
	if(word.length() <=0) 
		{
		return false;
		}
	Node* currNode = root;              
	bool valid = checkValid(word); 
	if(valid==false) 
		{
		return false; 
		}
	currNode = insertHelp(word, currNode); 
	if(currNode->endWord == true)
		{ 
		return false; 
		}
	currNode -> freqNode = freq;                
	currNode->endWord = true;   
	return true;
}


bool DictionaryTrie::find(std::string word) const
{
	std::unordered_map<char,int> Number2;
   	int numLetters= 26; 
	   
	for(int i =0; i< numLetters;i++){
		char curr = char(97 +i);
		Number2[curr] = i;
		Number2[' '] = 26;    
	}

	if(word.length() ==0 || root == NULL){
		return false;
	}

	Node* currNode = root;
	int index;
	size_t count = 0;

	for(int i= 0; i<numLetters; i++){
		char currWord = (char)word[i];
		index = Number2[currWord];
		if(currNode->vector[index]== NULL){
			if((count == word.length()) && (currNode->endWord == true)){
				return true;
			}
			return false;
		}
		count++;
		currNode = currNode->vector[index];   
	}
	bool returner = currNode->endWord; 
	return returner;
}


std::vector<std::string> DictionaryTrie::predictCompletions(
		std::string prefix, unsigned int num_completions)
{
	std::vector<std::string> words;
  	if((prefix.length() ==0) || (root == NULL) || (!(num_completions>0)) ){
		return words;
	}
  
	std:: queue <pair<Node*,std::string>> Tree;
	std::priority_queue<std::pair<Node*,std::string>,
		std::vector<std::pair<Node*,std::string>>,ComparePriority> tops;  
	Node* currNode = root;
	int index;
	
	for(size_t i = 0; i < prefix.length(); i++){
		if((prefix[i]!= ' ')&& (prefix[i] < 'a' || prefix[i]> 'z')){
			cout<< "Invalid Input. Please retry with correct input" 
			<< endl;
			return words;
		}
		char currWord = (char)prefix[i];
		index = Number[currWord];
		currNode = currNode -> vector[index];
	}
	
	Node* node = currNode; 
	std::pair<Node*,std::string> curr(node,prefix);
	Tree.push(curr);
	while(Tree.empty() == false){
		curr = Tree.front();
		Tree.pop(); 
		if(curr.first->endWord == true){
			tops.push(curr);
		} 
		size_t index1= 0;

		while(index1 < (curr.first->vector.size())){
			if((curr.first->vector[index1]) != nullptr){
				std::pair<Node*,std::string> child (curr.first->
				vector[index1],curr.second + Character[index1]);
				Tree.push(child);
			}  
			index1++;
		}
	}    
	size_t counter;
	for(size_t i=0; i < num_completions; i++){
		counter = 0;
		if(counter<tops.size()) {
			words.push_back(tops.top().second); 
			tops.pop();
			counter ++;
		}
	}
	return words;
}


DictionaryTrie::~DictionaryTrie(){
	deleteNodes(root);
}

void DictionaryTrie::deleteNodes(Node * n){
	int number = 27;
	if(n != NULL){
		int i = 0; 
		while(i < number){
			if(n->vector[i] != NULL){
				deleteNodes( n->vector[i]);

			}
			i++;
		}
		delete n;
	}
}

Node::~Node() {
    
}