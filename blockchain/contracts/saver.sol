pragma solidity ^0.8.0;
pragma abicoder v2;

contract saver{
    string[] simhashes;

    function addHash(string memory hash)public{
        simhashes.push(hash); 
    }
    function getAllHashes() public view returns (string[] memory){
        return simhashes;
    }

}