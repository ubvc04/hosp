// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title PatientRecords
 * @dev Smart contract for storing patient medical records on blockchain
 * @notice This contract stores hashes of medical records for integrity verification
 */
contract PatientRecords {
    
    // Contract owner (hospital admin)
    address public owner;
    
    // Authorized healthcare providers
    mapping(address => bool) public authorizedProviders;
    
    // Patient record structure
    struct MedicalRecord {
        bytes32 dataHash;           // Hash of the encrypted medical data
        uint256 timestamp;          // When the record was created
        address createdBy;          // Who created the record
        string recordType;          // Type: "VISIT", "BILL", "REPORT", "PATIENT_INFO"
        bool isActive;              // Whether record is active
    }
    
    // Patient ID => Array of medical records
    mapping(uint256 => MedicalRecord[]) public patientRecords;
    
    // Patient ID => Total record count
    mapping(uint256 => uint256) public patientRecordCount;
    
    // Audit log structure
    struct AuditLog {
        uint256 patientId;
        address accessor;
        string action;              // "CREATE", "READ", "UPDATE", "DELETE"
        uint256 timestamp;
        bytes32 recordHash;
    }
    
    // All audit logs
    AuditLog[] public auditLogs;
    
    // Events for tracking
    event RecordAdded(uint256 indexed patientId, bytes32 dataHash, string recordType, address indexed createdBy, uint256 timestamp);
    event RecordUpdated(uint256 indexed patientId, uint256 recordIndex, bytes32 newHash, address indexed updatedBy);
    event RecordDeactivated(uint256 indexed patientId, uint256 recordIndex, address indexed deactivatedBy);
    event ProviderAuthorized(address indexed provider, address indexed authorizedBy);
    event ProviderRevoked(address indexed provider, address indexed revokedBy);
    event AccessLogged(uint256 indexed patientId, address indexed accessor, string action);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }
    
    modifier onlyAuthorized() {
        require(authorizedProviders[msg.sender] || msg.sender == owner, "Not authorized");
        _;
    }
    
    /**
     * @dev Constructor sets the contract deployer as owner
     */
    constructor() {
        owner = msg.sender;
        authorizedProviders[msg.sender] = true;
    }
    
    /**
     * @dev Authorize a healthcare provider
     * @param provider Address of the provider to authorize
     */
    function authorizeProvider(address provider) external onlyOwner {
        require(provider != address(0), "Invalid address");
        require(!authorizedProviders[provider], "Already authorized");
        authorizedProviders[provider] = true;
        emit ProviderAuthorized(provider, msg.sender);
    }
    
    /**
     * @dev Revoke a healthcare provider's authorization
     * @param provider Address of the provider to revoke
     */
    function revokeProvider(address provider) external onlyOwner {
        require(provider != address(0), "Invalid address");
        require(authorizedProviders[provider], "Not authorized");
        require(provider != owner, "Cannot revoke owner");
        authorizedProviders[provider] = false;
        emit ProviderRevoked(provider, msg.sender);
    }
    
    /**
     * @dev Add a new medical record for a patient
     * @param patientId Unique patient identifier
     * @param dataHash Hash of the encrypted medical data
     * @param recordType Type of record (VISIT, BILL, REPORT, PATIENT_INFO)
     */
    function addRecord(
        uint256 patientId,
        bytes32 dataHash,
        string calldata recordType
    ) external onlyAuthorized {
        require(patientId > 0, "Invalid patient ID");
        require(dataHash != bytes32(0), "Invalid data hash");
        
        MedicalRecord memory newRecord = MedicalRecord({
            dataHash: dataHash,
            timestamp: block.timestamp,
            createdBy: msg.sender,
            recordType: recordType,
            isActive: true
        });
        
        patientRecords[patientId].push(newRecord);
        patientRecordCount[patientId]++;
        
        // Log the action
        _logAccess(patientId, "CREATE", dataHash);
        
        emit RecordAdded(patientId, dataHash, recordType, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Update an existing record (creates new version, deactivates old)
     * @param patientId Patient identifier
     * @param recordIndex Index of record to update
     * @param newDataHash New hash of updated data
     */
    function updateRecord(
        uint256 patientId,
        uint256 recordIndex,
        bytes32 newDataHash
    ) external onlyAuthorized {
        require(recordIndex < patientRecords[patientId].length, "Record not found");
        require(patientRecords[patientId][recordIndex].isActive, "Record is not active");
        
        // Deactivate old record
        patientRecords[patientId][recordIndex].isActive = false;
        
        // Add new record with same type
        string memory recordType = patientRecords[patientId][recordIndex].recordType;
        
        MedicalRecord memory newRecord = MedicalRecord({
            dataHash: newDataHash,
            timestamp: block.timestamp,
            createdBy: msg.sender,
            recordType: recordType,
            isActive: true
        });
        
        patientRecords[patientId].push(newRecord);
        patientRecordCount[patientId]++;
        
        _logAccess(patientId, "UPDATE", newDataHash);
        
        emit RecordUpdated(patientId, recordIndex, newDataHash, msg.sender);
    }
    
    /**
     * @dev Verify if a record hash matches what's stored on blockchain
     * @param patientId Patient identifier
     * @param recordIndex Index of the record
     * @param dataHash Hash to verify
     * @return bool True if hash matches
     */
    function verifyRecord(
        uint256 patientId,
        uint256 recordIndex,
        bytes32 dataHash
    ) external view returns (bool) {
        require(recordIndex < patientRecords[patientId].length, "Record not found");
        return patientRecords[patientId][recordIndex].dataHash == dataHash;
    }
    
    /**
     * @dev Get a specific record for a patient
     * @param patientId Patient identifier
     * @param recordIndex Index of the record
     */
    function getRecord(
        uint256 patientId,
        uint256 recordIndex
    ) external view onlyAuthorized returns (
        bytes32 dataHash,
        uint256 timestamp,
        address createdBy,
        string memory recordType,
        bool isActive
    ) {
        require(recordIndex < patientRecords[patientId].length, "Record not found");
        MedicalRecord storage record = patientRecords[patientId][recordIndex];
        return (
            record.dataHash,
            record.timestamp,
            record.createdBy,
            record.recordType,
            record.isActive
        );
    }
    
    /**
     * @dev Get all active records for a patient
     * @param patientId Patient identifier
     */
    function getPatientRecords(
        uint256 patientId
    ) external view onlyAuthorized returns (
        bytes32[] memory hashes,
        uint256[] memory timestamps,
        string[] memory recordTypes
    ) {
        uint256 count = patientRecords[patientId].length;
        uint256 activeCount = 0;
        
        // Count active records
        for (uint256 i = 0; i < count; i++) {
            if (patientRecords[patientId][i].isActive) {
                activeCount++;
            }
        }
        
        hashes = new bytes32[](activeCount);
        timestamps = new uint256[](activeCount);
        recordTypes = new string[](activeCount);
        
        uint256 j = 0;
        for (uint256 i = 0; i < count; i++) {
            if (patientRecords[patientId][i].isActive) {
                hashes[j] = patientRecords[patientId][i].dataHash;
                timestamps[j] = patientRecords[patientId][i].timestamp;
                recordTypes[j] = patientRecords[patientId][i].recordType;
                j++;
            }
        }
        
        return (hashes, timestamps, recordTypes);
    }
    
    /**
     * @dev Log access to patient records
     * @param patientId Patient identifier
     * @param action Action performed
     * @param recordHash Hash of record accessed
     */
    function logAccess(
        uint256 patientId,
        string calldata action,
        bytes32 recordHash
    ) external onlyAuthorized {
        _logAccess(patientId, action, recordHash);
    }
    
    /**
     * @dev Internal function to log access
     */
    function _logAccess(
        uint256 patientId,
        string memory action,
        bytes32 recordHash
    ) internal {
        AuditLog memory log = AuditLog({
            patientId: patientId,
            accessor: msg.sender,
            action: action,
            timestamp: block.timestamp,
            recordHash: recordHash
        });
        auditLogs.push(log);
        emit AccessLogged(patientId, msg.sender, action);
    }
    
    /**
     * @dev Get audit logs count
     */
    function getAuditLogCount() external view returns (uint256) {
        return auditLogs.length;
    }
    
    /**
     * @dev Get audit log by index
     */
    function getAuditLog(uint256 index) external view onlyAuthorized returns (
        uint256 patientId,
        address accessor,
        string memory action,
        uint256 timestamp,
        bytes32 recordHash
    ) {
        require(index < auditLogs.length, "Log not found");
        AuditLog storage log = auditLogs[index];
        return (log.patientId, log.accessor, log.action, log.timestamp, log.recordHash);
    }
    
    /**
     * @dev Get audit logs for a specific patient
     */
    function getPatientAuditLogs(
        uint256 patientId
    ) external view onlyAuthorized returns (
        address[] memory accessors,
        string[] memory actions,
        uint256[] memory timestamps
    ) {
        uint256 count = 0;
        
        // Count logs for patient
        for (uint256 i = 0; i < auditLogs.length; i++) {
            if (auditLogs[i].patientId == patientId) {
                count++;
            }
        }
        
        accessors = new address[](count);
        actions = new string[](count);
        timestamps = new uint256[](count);
        
        uint256 j = 0;
        for (uint256 i = 0; i < auditLogs.length; i++) {
            if (auditLogs[i].patientId == patientId) {
                accessors[j] = auditLogs[i].accessor;
                actions[j] = auditLogs[i].action;
                timestamps[j] = auditLogs[i].timestamp;
                j++;
            }
        }
        
        return (accessors, actions, timestamps);
    }
    
    /**
     * @dev Transfer contract ownership
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid address");
        authorizedProviders[owner] = false;
        owner = newOwner;
        authorizedProviders[newOwner] = true;
    }
}
