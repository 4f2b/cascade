import asyncio
import cascade


async def main():
    token_manager = cascade.TokenManager(master_password='your_secure_password_here')
    
    your_token = 'your_discord_token_here'
    
    is_valid = token_manager.validate_token_format(your_token)
    print(f'Token valid: {is_valid}')
    
    user_id = token_manager.extract_user_id(your_token)
    print(f'Extracted User ID: {user_id}')
    
    masked = token_manager.mask_token(your_token, visible_chars=4)
    print(f'Masked token: {masked}')
    
    encrypted = token_manager.encrypt_token(your_token)
    print(f'Encrypted token length: {len(encrypted)} bytes')
    
    decrypted = token_manager.decrypt_token(encrypted)
    print(f'Decryption successful: {decrypted == your_token}')
    
    fingerprint = cascade.FingerprintRandomizer()
    
    resolution = fingerprint.get_random_screen_resolution()
    print(f'Random screen resolution: {resolution}')
    
    timezone = fingerprint.get_random_timezone()
    print(f'Random timezone: {timezone}')
    
    canvas_noise = fingerprint.generate_canvas_noise()
    print(f'Canvas fingerprint: {canvas_noise[:32]}...')
    
    mouse_movements = fingerprint.generate_mouse_movement(steps=5)
    print(f'Generated {len(mouse_movements)} mouse movements')
    
    typing_pattern = fingerprint.generate_typing_pattern(text_length=20)
    print(f'Typing pattern: {typing_pattern["wpm"]} WPM')
    
    rate_limiter = cascade.SmartRateLimiter()
    
    print('\nSimulating API requests with smart rate limiting...')
    for i in range(5):
        await rate_limiter.wait_if_needed(f'/api/channels/123/messages')
        print(f'Request {i+1} sent with human-like delay')
        
        adaptive_delay = rate_limiter.get_adaptive_delay(f'/api/channels/123/messages')
        print(f'  Adaptive delay for next request: {adaptive_delay:.2f}s')
    
    session = cascade.Session(your_token, platform='desktop')
    
    @session.event
    async def on_ready(user):
        print(f'\nConnected as {user.username}')
        print(f'Platform: {session.get_platform_info()}')
    
    print('\nAll security features validated!')


if __name__ == '__main__':
    asyncio.run(main())
