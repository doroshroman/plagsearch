pragma solidity ^0.8.0;
pragma abicoder v2;

contract saver{
    string[] simhashes;
    string[] sha256hashes;

    function addHash(string memory simhash, string memory hashSha256) public{
        simhashes.push(simhash);
        sha256hashes.push(hashSha256);
    }

    function getAllHashes() public view returns (string[] memory, string[] memory){
        return (simhashes, sha256hashes);
    }

}