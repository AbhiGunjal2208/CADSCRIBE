# Project-Centric Schema Refactor Guide

## 🎯 Overview

This document outlines the complete refactoring of the MongoDB schema from a flat message-based structure to a project-centric architecture. The new schema organizes all data around projects, providing better data organization, querying capabilities, and scalability.

## 🏗️ New Database Structure

### Collections Overview
```
MongoDB Database
├── projects (root documents)
├── messages (chat history per project)
├── files (S3 file tracking per project)
├── logs (processing logs per project)
└── users (unchanged)
```

### 1. Projects Collection
**Purpose**: Root documents that link all project-related data

```javascript
{
  "_id": ObjectId,
  "project_id": "project-123",           // Unique identifier
  "project_name": "Gearbox Assembly",    // Human-readable name
  "created_by": "user-456",              // User ID who created it
  "created_at": ISODate("2025-10-11T12:24:35Z"),
  "updated_at": ISODate("2025-10-11T12:26:10Z"),
  "current_version": 3,                  // Latest script version
  "ai_model_used": "Gemini",            // AI model used for generation
  "status": "completed",                 // ["draft", "processing", "completed", "error"]
  "latest_s3_input": "s3://bucket/input/project_gearbox/project_gearbox_v3.py",
  "latest_s3_output": [                  // Array of output file S3 paths
      "s3://bucket/output/project_gearbox/MyHeadlessModel.STL",
      "s3://bucket/output/project_gearbox/MyHeadlessModel.STEP"
  ],
  "metadata": {
      "description": "Parametric gearbox CAD model",
      "confidence": 0.93,
      "generation_time": 2.45,
      "parameters": {...}
  }
}
```

**Indexes**:
- `project_id` (unique)
- `created_by`
- `updated_at` (descending)
- `created_by + updated_at` (compound)

### 2. Messages Collection
**Purpose**: Store chat history and AI conversations linked to projects

```javascript
{
  "_id": ObjectId,
  "project_id": "project-123",           // Links to projects collection
  "user_id": "user-456",
  "role": "assistant",                   // "user" | "assistant" | "system"
  "content": "Generated CAD model...",
  "timestamp": ISODate("2025-10-11T12:24:35Z"),
  "metadata": {
      "source_model": "Gemini",
      "confidence": 0.95,
      "response_time": 2.45,
      "s3_url": "s3://bucket/input/project_gearbox/project_gearbox_v3.py",
      "version": 3
  },
  "created_at": ISODate("2025-10-11T12:24:35Z"),
  "updated_at": ISODate("2025-10-11T12:24:35Z")
}
```

**Indexes**:
- `project_id`
- `timestamp`
- `project_id + timestamp` (compound)
- `user_id`

### 3. Files Collection
**Purpose**: Track all uploaded/generated files by project with versioning

```javascript
{
  "_id": ObjectId,
  "project_id": "project-123",
  "version": 3,
  "file_type": "input",                  // "input", "output", "log", "processed"
  "s3_path": "s3://bucket/input/project_gearbox/project_gearbox_v3.py",
  "timestamp": ISODate("2025-10-11T12:24:35Z"),
  "metadata": {
      "file_name": "project_gearbox_v3.py",
      "ai_model": "Gemini",
      "uploaded_by": "user-456",
      "generated_by": "cadscribe-ai",
      "file_size": 2048,
      "content_type": "text/x-python"
  },
  "created_at": ISODate("2025-10-11T12:24:35Z"),
  "updated_at": ISODate("2025-10-11T12:24:35Z")
}
```

**Indexes**:
- `project_id`
- `version`
- `file_type`
- `project_id + version` (compound, descending)
- `project_id + file_type` (compound)

### 4. Logs Collection
**Purpose**: Store worker execution logs from processing

```javascript
{
  "_id": ObjectId,
  "project_id": "project-123",
  "version": 3,
  "s3_log_path": "s3://bucket/logs/project_gearbox/project_gearbox_info_20251011_122435.log",
  "log_summary": "Model generated successfully.",
  "timestamp": ISODate("2025-10-11T12:25:30Z"),
  "metadata": {
      "processing_time": 45.2,
      "worker_id": "worker-001",
      "exit_code": 0
  },
  "created_at": ISODate("2025-10-11T12:25:30Z"),
  "updated_at": ISODate("2025-10-11T12:25:30Z")
}
```

**Indexes**:
- `project_id`
- `version`
- `timestamp` (descending)
- `project_id + timestamp` (compound, descending)

## 🔄 Migration Process

### Migration Script
Location: `backend/scripts/migrate_to_project_schema.py`

**Usage**:
```bash
# Dry run to analyze existing data
python migrate_to_project_schema.py --dry-run

# Execute migration
python migrate_to_project_schema.py

# Verify migration results
python migrate_to_project_schema.py --verify

# Rollback (DANGEROUS - use with caution)
python migrate_to_project_schema.py --rollback
```

**Migration Steps**:
1. **Analyze Legacy Data**: Scan existing `chat_messages` collection
2. **Group by Project**: Group messages by `project_id` (create default projects for orphaned messages)
3. **Create Projects**: Generate project documents with metadata extracted from messages
4. **Migrate Messages**: Move messages to new `messages` collection with proper linking
5. **Create File Records**: Extract S3 references from message metadata and create file records
6. **Verify Results**: Validate migration success and data integrity

## 🚀 New Services

### ProjectService
Location: `backend/services/project_service.py`

**Key Methods**:
```python
# Project operations
create_project(project_data: Dict) -> str
get_project_by_id(project_id: str) -> Optional[Dict]
get_user_projects(user_id: str) -> List[Dict]
update_project(project_id: str, update_data: Dict) -> bool
delete_project(project_id: str) -> bool

# Message operations
create_message(message_data: Dict) -> str
get_project_messages(project_id: str) -> List[Dict]

# File operations
create_file_record(file_data: Dict) -> str
get_project_files(project_id: str, file_type: Optional[str]) -> List[Dict]
get_latest_file_by_type(project_id: str, file_type: str) -> Optional[Dict]

# Log operations
create_log_record(log_data: Dict) -> str
get_project_logs(project_id: str) -> List[Dict]

# Comprehensive operations
get_project_with_data(project_id: str) -> Optional[Dict]
update_project_version(project_id: str, version: int) -> bool
mark_project_completed(project_id: str, output_files: List[str]) -> bool
```

## 🔌 Updated API Endpoints

### New Project Data Endpoints
Location: `backend/routes/project_data.py`

```http
GET    /api/projects/{project_id}/messages     # Get project chat history
GET    /api/projects/{project_id}/files        # Get project files (with optional type filter)
GET    /api/projects/{project_id}/logs         # Get project processing logs
GET    /api/projects/{project_id}/complete     # Get complete project data
GET    /api/projects/{project_id}/summary      # Get project summary with counts
```

### Updated Existing Endpoints
- **AI Chat**: Now creates/updates projects automatically
- **Project Management**: Uses new project service for CRUD operations
- **Script Management**: Updated to use project-centric verification

## 🔧 Service Integration Updates

### AI Service Updates
- **Project Creation**: Automatically creates projects for chat sessions
- **File Tracking**: Creates file records when uploading to S3
- **Project Updates**: Updates project version and status after generation

### S3 Service Updates
- **File Records**: Creates database records for all S3 operations
- **Project Linking**: Links S3 operations to specific projects and versions
- **Metadata Tracking**: Enhanced metadata storage for better tracking

## 📊 Benefits of New Schema

### 1. **Better Data Organization**
- Clear hierarchical structure with projects as root entities
- Logical grouping of related data (messages, files, logs)
- Easier to understand and maintain

### 2. **Improved Query Performance**
- Targeted indexes for common query patterns
- Efficient joins using project_id
- Better support for pagination and filtering

### 3. **Enhanced Scalability**
- Horizontal scaling potential with project-based sharding
- Reduced document size in individual collections
- Better memory usage patterns

### 4. **Simplified Frontend Integration**
- Single project_id to fetch all related data
- Structured API responses with consistent format
- Better support for real-time updates

### 5. **Version Management**
- Clear version tracking across all file types
- Easy to query specific versions or latest versions
- Better support for rollback operations

## 🔍 Query Examples

### Get Complete Project Data
```javascript
// Single query to get project with all related data
const projectData = await project_service.get_project_with_data("project-123");

// Result structure:
{
  "project": {...},           // Project document
  "messages": [...],          // All chat messages
  "files": [...],            // All files with versions
  "files_by_type": {         // Files grouped by type
    "input": [...],
    "output": [...],
    "log": [...],
    "processed": [...]
  },
  "logs": [...]              // Processing logs
}
```

### Get Latest Files by Type
```javascript
// Get latest input file for a project
const latestScript = await project_service.get_latest_file_by_type(
  "project-123", 
  "input"
);

// Get all output files for a project
const outputFiles = await project_service.get_project_files(
  "project-123", 
  "output"
);
```

### Project Status Tracking
```javascript
// Update project after AI generation
await project_service.update_project_version(
  "project-123",
  4,                    // New version
  "Gemini",            // AI model used
  "s3://bucket/..."    // S3 input path
);

// Mark project as completed with outputs
await project_service.mark_project_completed(
  "project-123",
  ["s3://bucket/output/model.stl", "s3://bucket/output/model.step"]
);
```

## 🛡️ Data Integrity & Validation

### Schema Validation
- **TypedDict Models**: Strong typing for all document structures
- **Enum Validation**: Controlled vocabularies for status, roles, file types
- **Required Fields**: Proper validation of mandatory fields

### Referential Integrity
- **Project Linking**: All messages, files, and logs must reference valid projects
- **User Ownership**: Projects are owned by specific users with proper access control
- **Version Consistency**: File versions must be consistent within projects

### Error Handling
- **Graceful Degradation**: System continues to work if some collections are unavailable
- **Transaction Safety**: Atomic operations where possible
- **Rollback Support**: Migration can be safely rolled back if needed

## 🚀 Deployment Considerations

### Pre-Deployment
1. **Backup Database**: Create full backup of existing MongoDB data
2. **Test Migration**: Run migration script on copy of production data
3. **Verify Indexes**: Ensure all required indexes are created
4. **Update Dependencies**: Ensure all services use new project service

### Deployment Steps
1. **Deploy New Code**: Update backend with new schema and services
2. **Run Migration**: Execute migration script during maintenance window
3. **Verify Data**: Check migration results and data integrity
4. **Update Frontend**: Deploy frontend changes to use new API endpoints
5. **Monitor Performance**: Watch for any performance issues with new queries

### Post-Deployment
1. **Monitor Logs**: Check for any errors related to new schema
2. **Performance Metrics**: Monitor query performance and response times
3. **User Testing**: Verify all functionality works as expected
4. **Cleanup**: Remove legacy code and unused collections after verification period

## 📈 Performance Optimizations

### Database Indexes
- **Compound Indexes**: Optimized for common query patterns
- **Sparse Indexes**: For optional fields to save space
- **TTL Indexes**: For automatic cleanup of old log entries (if needed)

### Query Optimization
- **Projection**: Only fetch required fields in queries
- **Pagination**: Proper limit/skip for large result sets
- **Aggregation**: Use MongoDB aggregation pipeline for complex queries

### Caching Strategy
- **Project Metadata**: Cache frequently accessed project information
- **File Lists**: Cache file listings for active projects
- **User Projects**: Cache user's project list with TTL

## 🔮 Future Enhancements

### Planned Features
1. **Project Templates**: Reusable project configurations
2. **Collaboration**: Multi-user project access and permissions
3. **Project Analytics**: Usage statistics and performance metrics
4. **Automated Cleanup**: Scheduled cleanup of old versions and logs
5. **Project Export**: Export complete project data for backup/sharing

### Schema Extensions
- **Project Tags**: Categorization and filtering
- **Project Dependencies**: Link related projects
- **Workflow States**: More granular status tracking
- **Audit Trail**: Complete change history for projects

## ✅ Migration Checklist

### Pre-Migration
- [ ] Backup production database
- [ ] Test migration script on development data
- [ ] Verify all new services are properly tested
- [ ] Update API documentation
- [ ] Prepare rollback plan

### Migration Execution
- [ ] Put system in maintenance mode
- [ ] Run migration script with verification
- [ ] Check data integrity and completeness
- [ ] Verify all indexes are created
- [ ] Test critical user flows

### Post-Migration
- [ ] Monitor system performance
- [ ] Check error logs for issues
- [ ] Verify frontend functionality
- [ ] Update monitoring dashboards
- [ ] Document any issues and resolutions

The project-centric schema refactor provides a solid foundation for future growth and better user experience while maintaining backward compatibility during the transition period.
