# 🔧 Persistent Authentication Setup Guide

Complete step-by-step guide to enable persistent login in your RequirementIQ app.

## ⚡ 5-Minute Quick Setup

### Step 1: Update .env File (1 minute)

Add these two lines to your `.env` file:

```bash
# JWT Secret Key for token signing (MUST change in production!)
JWT_SECRET_KEY=dev-secret-key-change-this-in-production

# Token expiry settings
TOKEN_EXPIRY_HOURS=24
REFRESH_TOKEN_EXPIRY_DAYS=30
```

### Step 2: Restart Streamlit App (1 minute)

The app will automatically:
- Check for JWT_SECRET_KEY
- Initialize auth_tokens table in database
- Enable persistent login

```bash
streamlit run AI_BA_PM/app.py
```

### Step 3: Test Persistent Login (3 minutes)

1. **Sign in** with test account
2. Check "Keep me signed in" box (checked by default)
3. Click "Sign In →"
4. **Refresh the page** (Ctrl+R or Cmd+R)
5. ✅ You should see the dashboard without re-entering credentials

**Done!** Your app now has persistent login 🎉

---

## 🔐 Production Setup

### Step 1: Generate Strong JWT Secret

Use Python to generate a cryptographically secure secret key:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Example output:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z
```

### Step 2: Add to Production .env

```bash
# ⚠️ PRODUCTION CRITICAL - CHANGE THIS!
JWT_SECRET_KEY=<paste-the-generated-secret-here>

# Adjust expiry based on your security requirements
TOKEN_EXPIRY_HOURS=24          # Session expires after 24 hours
REFRESH_TOKEN_EXPIRY_DAYS=30    # Refresh token valid for 30 days
```

### Step 3: Database Verification

Verify the `auth_tokens` table was created:

```sql
-- Connect to your MySQL database
mysql> DESCRIBE auth_tokens;

-- Expected output:
-- +-----------+-----------+------+-----+-------------------+-------------------+
-- | Field     | Type      | Null | Key | Default           | Extra             |
-- +-----------+-----------+------+-----+-------------------+-------------------+
-- | id        | int       | NO   | PRI | NULL              | auto_increment    |
-- | user_id   | varchar(36)| NO  | MUL | NULL              |                   |
-- | token_hash| varchar(64)| NO  | UNI | NULL              |                   |
-- | token_type| varchar(20)| NO  |     | NULL              |                   |
-- | created_at| timestamp | NO  |     | CURRENT_TIMESTAMP |                   |
-- | expires_at| datetime  | NO  |     | NULL              |                   |
-- +-----------+-----------+------+-----+-------------------+-------------------+
```

### Step 4: Test & Monitor

Check active tokens:
```sql
SELECT COUNT(*) as active_tokens 
FROM auth_tokens 
WHERE expires_at > NOW();
```

---

## 📝 Environment Variables Reference

### JWT_SECRET_KEY (REQUIRED)

**What it does:** Signs and verifies JWT tokens  
**Default:** Warning shown if not set  
**Example (dev):** `dev-secret-key-change-this`  
**Example (prod):** `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

**⚠️ CRITICAL SECURITY:**
- Change this in production **immediately**
- Never commit to git
- Use 32+ character random string
- Regenerate periodically

### TOKEN_EXPIRY_HOURS (Optional)

**What it does:** How long access token is valid  
**Default:** 24 hours  
**Range:** 1-720 hours (1 hour to 30 days)  

**Examples:**
- Small team (high trust): 168 hours (7 days)
- Standard SaaS: 24 hours (1 day)
- High security: 4 hours
- API tokens: 1 hour

### REFRESH_TOKEN_EXPIRY_DAYS (Optional)

**What it does:** How long user stays "remembered"  
**Default:** 30 days  
**Range:** 1-365 days  

**Examples:**
- High security: 7 days
- Standard: 30 days  
- Long-tail users: 90 days

---

## 🔍 Verification Checklist

After setup, verify:

- [ ] `.env` file has JWT_SECRET_KEY set
  ```bash
  grep JWT_SECRET_KEY .env
  ```

- [ ] App starts without "SECURITY WARNING"
  ```bash
  streamlit run AI_BA_PM/app.py
  ```

- [ ] Database table exists
  ```sql
  SELECT COUNT(*) FROM auth_tokens;
  -- Should return: 0
  ```

- [ ] Can sign in and stay logged in after refresh
  1. Sign in with test account
  2. Check "Keep me signed in"
  3. Refresh page
  4. ✅ Should be logged in

- [ ] Logout works properly
  1. Click "Log Out"
  2. Refresh page
  3. ✅ Should be at login page

- [ ] Token expiration works
  1. (Temporarily set TOKEN_EXPIRY_HOURS=0.01 for testing)
  2. Sign in
  3. Wait 40 seconds
  4. Refresh page
  5. ✅ Should be logged out

---

## 🐛 Troubleshooting

### Issue: "SECURITY WARNING: Using default JWT_SECRET_KEY"

**Cause:** JWT_SECRET_KEY not set in .env  
**Solution:**
```bash
# Generate a key
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))" >> .env

# Verify it's set
grep JWT_SECRET_KEY .env

# Restart app
streamlit run AI_BA_PM/app.py
```

### Issue: "Cannot connect to auth_tokens table"

**Cause:** Table not created or database error  
**Solution:**
```bash
# Check if table exists
mysql -u <user> -p <database> -e "DESCRIBE auth_tokens;"

# If table doesn't exist, manually create it:
mysql -u <user> -p <database> < database/auth_token_schema.sql

# Or restart the app (auto-creates on startup)
streamlit run AI_BA_PM/app.py
```

### Issue: "Token signature invalid" on login

**Cause:** JWT_SECRET_KEY changed or corrupted  
**Solution:**
- Clear all tokens from database
  ```sql
  DELETE FROM auth_tokens;
  ```
- All users must log in again
- Check that JWT_SECRET_KEY in .env matches running key

### Issue: Users logged out after server restart

**Cause:** Tokens stored in-memory, or JWT_SECRET_KEY changed  
**Solution:**
- Tokens are in database (persistent)
- Check that JWT_SECRET_KEY is same in .env
- Verify auth_tokens table has user tokens

### Issue: "Auto-login not working"

**Cause:** Token cache not set or browser localStorage disabled  
**Solution:**
1. Ensure browser allows localStorage
2. Check browser DevTools → Application → LocalStorage
3. Manual test:
   ```python
   from services.cookie_manager import SimpleAuthCache
   SimpleAuthCache.cache_auth_token("test_token")
   print(SimpleAuthCache.get_cached_auth_token())  # Should return "test_token"
   ```

---

## 📊 Database Management

### View Active Sessions

```sql
SELECT 
  u.email,
  u.full_name,
  COUNT(*) as active_tokens,
  MAX(a.created_at) as last_login
FROM users u
LEFT JOIN auth_tokens a ON u.id = a.user_id AND a.expires_at > NOW()
WHERE a.id IS NOT NULL
GROUP BY u.id
ORDER BY last_login DESC;
```

### Cleanup Expired Tokens

```sql
-- Periodic cleanup (remove tokens older than 60 days)
DELETE FROM auth_tokens 
WHERE expires_at < DATE_SUB(NOW(), INTERVAL 60 DAY);

-- Check how many will be deleted
SELECT COUNT(*) as expired_tokens
FROM auth_tokens 
WHERE expires_at < NOW();
```

### Logout All Users (Emergency)

```sql
-- Revoke all refresh tokens (forces re-login)
DELETE FROM auth_tokens WHERE token_type = 'refresh';

-- Verify all cleared
SELECT COUNT(*) FROM auth_tokens;
-- Should return: 0
```

---

## 🚀 Production Checklist

- [ ] **Generated strong JWT_SECRET_KEY**
  - Not using default value
  - 32+ character random string

- [ ] **Set all environment variables**
  - JWT_SECRET_KEY
  - TOKEN_EXPIRY_HOURS
  - REFRESH_TOKEN_EXPIRY_DAYS

- [ ] **Database configured**
  - auth_tokens table exists
  - Indexes created (auto-created)
  - Sufficient storage for token volume

- [ ] **Tested locally**
  - Persistent login works
  - Token expiration works
  - Logout revokes tokens
  - Auto-login on refresh works

- [ ] **Security review**
  - JWT_SECRET_KEY not in git
  - HTTPS enabled (Streamlit Cloud does this)
  - Database credentials secure
  - No hardcoded secrets

- [ ] **Monitoring set up**
  - Alert on failed logins
  - Monitor auth_tokens table size
  - Track active sessions

- [ ] **Deployment verification**
  - Test sign-in in production
  - Test persistent login
  - Test logout
  - Check logs for errors

---

## 🔄 Updating Secret Key (Rotation)

If you need to rotate the JWT_SECRET_KEY in production:

```bash
# 1. Generate new secret
python3 -c "import secrets; print(secrets.token_hex(32))"

# 2. In production, do rolling update:
#    - Keep old secret in OLD_JWT_SECRET_KEY
#    - Accept tokens signed with either
#    - Update app to accept both

# 3. After grace period, remove old secret
#    - All users re-authenticate

# 4. Update .env
JWT_SECRET_KEY=<new-secret>
```

---

## 📚 Files Modified/Created

### New Files
- `services/secure_auth_service.py` - JWT token management
- `services/cookie_manager.py` - Browser storage management
- `PERSISTENT_AUTH_GUIDE.md` - This comprehensive guide
- `PERSISTENT_AUTH_SETUP.md` - This setup guide

### Updated Files
- `app.py` - Persistent login flow + auto-login
- `database/schema.sql` - (optional) auth_tokens table

### Configuration Files
- `.env` - Add JWT_SECRET_KEY and token expiry

---

## ✅ Success Criteria

You'll know setup is complete when:

✅ App starts without "SECURITY WARNING"  
✅ auth_tokens table created automatically  
✅ Can sign in and stay logged in after refresh  
✅ Logout revokes token from database  
✅ Token expires after configured time  
✅ Auto-login works silently on page load  
✅ Users see "Welcome back!" toast on re-login  

---

## 🆘 Need Help?

1. **Check logs:**
   ```bash
   streamlit run AI_BA_PM/app.py --logger.level=debug
   ```

2. **Review database:**
   ```sql
   SELECT * FROM auth_tokens ORDER BY created_at DESC LIMIT 10;
   ```

3. **Test token validation:**
   ```python
   from services.secure_auth_service import verify_token
   is_valid, payload, msg = verify_token(token_string)
   print(f"Valid: {is_valid}, Message: {msg}")
   ```

---

**Setup Time:** ~5 minutes  
**Difficulty:** ⭐ Easy  
**Security Level:** ⭐⭐⭐⭐⭐ Enterprise-Grade
