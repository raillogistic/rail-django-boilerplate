# Custom Mutation Documentation - Blog Post Publication

## Overview

This document provides comprehensive documentation for the custom mutation implementation in the Django GraphQL blog application. The mutation system enables complex business logic operations through decorated model methods that are automatically exposed as GraphQL mutations.

## Mutation Implementation: `publish_post`

### Purpose
The `publish_post` mutation handles the complete publication workflow for blog posts, including validation, status updates, scheduling, and subscriber notifications.

### Method Signature
```python
@mutation(description="Publish a blog post with validation and status updates")
def publish_post(self, publish_date: str = None, notify_subscribers: bool = True) -> dict:
```

### Input Parameters

#### `publish_date` (Optional)
- **Type**: `str`
- **Format**: ISO 8601 datetime string (e.g., "2024-01-15T10:00:00Z")
- **Default**: `None` (publishes immediately)
- **Purpose**: Allows scheduled publishing for future dates
- **Validation**: Must be a valid ISO format and cannot be in the past

#### `notify_subscribers` (Optional)
- **Type**: `bool`
- **Default**: `True`
- **Purpose**: Controls whether active subscribers are notified about the new publication
- **Business Logic**: Only triggers notifications for posts transitioning from non-published to published status

### Expected Outputs

#### Success Response
```json
{
    "success": true,
    "message": "Post 'Example Title' published successfully",
    "post_id": 123,
    "published_at": "2024-01-15T10:00:00+00:00",
    "previous_status": "draft",
    "current_status": "published",
    "notification_result": {
        "notified_count": 150,
        "notification_sent": true
    },
    "view_count": 0
}
```

#### Validation Error Response
```json
{
    "success": false,
    "message": "Validation error: Post content must be at least 50 characters long",
    "post_id": 123,
    "error_type": "validation_error"
}
```

#### System Error Response
```json
{
    "success": false,
    "message": "Unexpected error during publication: Database connection failed",
    "post_id": 123,
    "error_type": "system_error"
}
```

## Validation Logic

### Pre-Publication Checks

1. **Title Validation**
   - Ensures post has a non-empty title
   - Trims whitespace and validates content exists
   - Error: "Post title is required for publication"

2. **Content Validation**
   - Requires minimum 50 characters of content
   - Strips whitespace before length check
   - Error: "Post content must be at least 50 characters long"

3. **Category Assignment**
   - Verifies post has an assigned category
   - Error: "Post must have a category assigned"

4. **Status Validation**
   - Prevents publishing of archived posts
   - Error: "Cannot publish archived posts"

5. **Date Validation**
   - Validates ISO format for scheduled publishing
   - Ensures future dates only for scheduling
   - Error: "Publish date cannot be in the past" or "Invalid publish date format"

## Business Logic Implementation

### Publication Workflow

1. **Status Transition**
   - Captures previous status for tracking
   - Updates status to 'published'
   - Resets view count for newly published posts

2. **Timestamp Management**
   - Sets `published_at` to current time or scheduled time
   - Maintains creation and update timestamps

3. **Subscriber Notification**
   - Queries active subscribers when `notify_subscribers=True`
   - Only notifies for status transitions to 'published'
   - Gracefully handles notification failures
   - Returns notification statistics

### Error Handling Strategy

#### Exception Hierarchy
- **ValueError**: Input validation and business rule violations
- **Generic Exception**: System-level errors (database, network, etc.)

#### Error Response Structure
- Consistent error format with success flag
- Descriptive error messages for debugging
- Error type classification for client handling
- Post ID included for tracking

## GraphQL Integration

### Decorator Configuration
```python
@mutation(description="Publish a blog post with validation and status updates")
```

The `@mutation` decorator automatically:
- Registers the method as a GraphQL mutation
- Generates appropriate input/output types
- Handles parameter conversion from GraphQL to Python
- Manages return value serialization

### Generated GraphQL Schema
```graphql
type Mutation {
    publishPost(
        id: ID!
        publishDate: String
        notifySubscribers: Boolean = true
    ): PublishPostPayload
}

type PublishPostPayload {
    success: Boolean!
    message: String!
    postId: ID!
    publishedAt: String
    previousStatus: String
    currentStatus: String
    notificationResult: NotificationResult
    viewCount: Int
    errorType: String
}
```

## Usage Examples

### Immediate Publication
```graphql
mutation {
    publishPost(id: "123", notifySubscribers: true) {
        success
        message
        postId
        publishedAt
        currentStatus
        notificationResult {
            notifiedCount
            notificationSent
        }
    }
}
```

### Scheduled Publication
```graphql
mutation {
    publishPost(
        id: "123"
        publishDate: "2024-01-15T10:00:00Z"
        notifySubscribers: false
    ) {
        success
        message
        publishedAt
        previousStatus
        currentStatus
    }
}
```

## Security Considerations

### Access Control
- Mutation respects model-level security decorators
- User permissions validated before execution
- Audit logging for publication operations

### Input Sanitization
- All string inputs are validated and sanitized
- Date parsing uses secure ISO format validation
- Boolean parameters have explicit type checking

## Performance Considerations

### Database Operations
- Single save operation per mutation
- Efficient subscriber count query
- Minimal database round trips

### Notification System
- Asynchronous notification handling recommended
- Graceful degradation on notification failures
- Subscriber query optimization

## Testing Strategy

### Unit Tests
- Validation logic testing
- Error condition handling
- Business rule enforcement

### Integration Tests
- GraphQL mutation execution
- Database state verification
- Notification system integration

### Example Test Cases
```python
def test_publish_post_success():
    # Test successful publication with all validations passing
    
def test_publish_post_validation_errors():
    # Test various validation failure scenarios
    
def test_publish_post_scheduled():
    # Test scheduled publication functionality
    
def test_publish_post_notification():
    # Test subscriber notification logic
```

## Monitoring and Logging

### Metrics to Track
- Publication success/failure rates
- Validation error frequencies
- Notification delivery statistics
- Performance timing metrics

### Log Levels
- INFO: Successful publications
- WARNING: Validation failures
- ERROR: System errors during publication
- DEBUG: Detailed execution flow

## Future Enhancements

### Potential Improvements
1. **Batch Publication**: Support for publishing multiple posts
2. **Workflow Integration**: Integration with approval workflows
3. **Rich Notifications**: HTML email templates and push notifications
4. **Analytics Integration**: Publication metrics and engagement tracking
5. **Content Validation**: Advanced content quality checks

### API Evolution
- Backward compatibility considerations
- Version management for mutation changes
- Deprecation strategy for old mutation formats

---

**Document Version**: 1.0  
**Last Updated**: January 2024  
**Author**: Rail Logistic Development Team  
**Review Status**: Technical Review Complete