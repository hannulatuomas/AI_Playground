import { WSSecurityService } from '../../src/main/services/WSSecurityService';

describe('WSSecurityService', () => {
  let service: WSSecurityService;

  beforeEach(() => {
    service = new WSSecurityService();
  });

  describe('Security Header Generation', () => {
    test('should generate security header with username token (text)', () => {
      const header = service.generateSecurityHeader({
        username: 'testuser',
        password: 'testpass',
        passwordType: 'PasswordText',
        timestamp: false,
      });

      expect(header).toContain('<wsse:Security');
      expect(header).toContain('<wsse:UsernameToken');
      expect(header).toContain('<wsse:Username>testuser</wsse:Username>');
      expect(header).toContain('PasswordText');
      expect(header).toContain('testpass');
    });

    test('should generate security header with password digest', () => {
      const header = service.generateSecurityHeader({
        username: 'testuser',
        password: 'testpass',
        passwordType: 'PasswordDigest',
        nonce: true,
        timestamp: false,
      });

      expect(header).toContain('<wsse:Security');
      expect(header).toContain('PasswordDigest');
      expect(header).toContain('<wsse:Nonce');
      expect(header).toContain('<wsu:Created>');
      expect(header).not.toContain('testpass'); // Password should be hashed
    });

    test('should generate timestamp when requested', () => {
      const header = service.generateSecurityHeader({
        timestamp: true,
        timestampTTL: 300,
      });

      expect(header).toContain('<wsu:Timestamp');
      expect(header).toContain('<wsu:Created>');
      expect(header).toContain('<wsu:Expires>');
    });

    test('should include nonce when requested', () => {
      const header = service.generateSecurityHeader({
        username: 'testuser',
        password: 'testpass',
        passwordType: 'PasswordText',
        nonce: true,
      });

      expect(header).toContain('<wsse:Nonce');
      expect(header).toContain('EncodingType');
    });
  });

  describe('Security Profiles', () => {
    test('should return security profiles', () => {
      const profiles = service.getSecurityProfiles();

      expect(profiles).toBeInstanceOf(Array);
      expect(profiles.length).toBeGreaterThan(0);
      
      profiles.forEach(profile => {
        expect(profile).toHaveProperty('name');
        expect(profile).toHaveProperty('description');
        expect(profile).toHaveProperty('options');
      });
    });

    test('should have username token text profile', () => {
      const profiles = service.getSecurityProfiles();
      const textProfile = profiles.find(p => p.name.includes('Text'));

      expect(textProfile).toBeDefined();
      expect(textProfile?.options.passwordType).toBe('PasswordText');
    });

    test('should have password digest profile', () => {
      const profiles = service.getSecurityProfiles();
      const digestProfile = profiles.find(p => p.name.includes('Digest'));

      expect(digestProfile).toBeDefined();
      expect(digestProfile?.options.passwordType).toBe('PasswordDigest');
    });
  });

  describe('SOAP Envelope Enhancement', () => {
    test('should add security to SOAP envelope', () => {
      const envelope = `<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header/>
  <soap:Body>
    <GetUser/>
  </soap:Body>
</soap:Envelope>`;

      const secured = service.addSecurityToEnvelope(envelope, {
        username: 'user',
        password: 'pass',
        passwordType: 'PasswordText',
      });

      expect(secured).toContain('<wsse:Security');
      expect(secured).toContain('<wsse:UsernameToken');
      expect(secured.indexOf('<wsse:Security')).toBeLessThan(secured.indexOf('<soap:Body'));
    });
  });

  describe('Security Header Validation', () => {
    test('should validate complete security header', () => {
      const result = service.validateSecurityHeader({
        username: 'user',
        password: 'pass',
        passwordType: 'PasswordText',
      });

      expect(result.valid).toBe(true);
      expect(result.errors).toBeUndefined();
    });

    test('should detect missing username', () => {
      const result = service.validateSecurityHeader({
        password: 'pass',
      } as any);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Username is required');
    });

    test('should detect missing password', () => {
      const result = service.validateSecurityHeader({
        username: 'user',
      } as any);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password is required');
    });

    test('should validate password digest requirements', () => {
      const result = service.validateSecurityHeader({
        username: 'user',
        password: 'pass',
        passwordType: 'PasswordDigest',
      });

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Nonce is required for PasswordDigest');
      expect(result.errors).toContain('Created timestamp is required for PasswordDigest');
    });
  });

  describe('Basic Auth', () => {
    test('should create basic auth header', () => {
      const auth = service.createBasicAuth('user', 'pass');

      expect(auth).toContain('Basic ');
      expect(auth).toBe('Basic ' + Buffer.from('user:pass').toString('base64'));
    });
  });
});
