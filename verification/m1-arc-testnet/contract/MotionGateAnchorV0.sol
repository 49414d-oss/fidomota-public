// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MotionGateAnchorV0 {
    event Anchored(bytes32 indexed root, bytes32 indexed meta, address indexed who, uint256 ts);

    function anchor(bytes32 root, bytes32 meta) external {
        emit Anchored(root, meta, msg.sender, block.timestamp);
    }
}
