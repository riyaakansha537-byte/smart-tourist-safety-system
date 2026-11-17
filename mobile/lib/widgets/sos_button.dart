// ============================================================
// Smart Tourist Safety and Emergency Response System
// Widget: Glowing Pulsing SOS Emergency Button
// ============================================================

import 'package:flutter/material.dart';
import '../config/app_theme.dart';

class SosButton extends StatefulWidget {
  final VoidCallback onPressed;
  final bool isLoading;
  final double size;

  const SosButton({
    super.key,
    required this.onPressed,
    this.isLoading = false,
    this.size = 140.0,
  });

  @override
  State<SosButton> createState() => _SosButtonState();
}

class _SosButtonState extends State<SosButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1600),
    )..repeat(reverse: true);

    _scaleAnimation = Tween<double>(begin: 0.96, end: 1.04).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _glowAnimation = Tween<double>(begin: 12.0, end: 32.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _pulseController,
      builder: (context, child) {
        return Transform.scale(
          scale: widget.isLoading ? 1.0 : _scaleAnimation.value,
          child: Container(
            width: widget.size,
            height: widget.size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: AppTheme.danger.withOpacity(0.55),
                  blurRadius: _glowAnimation.value,
                  spreadRadius: 4,
                ),
                BoxShadow(
                  color: Colors.redAccent.withOpacity(0.3),
                  blurRadius: _glowAnimation.value * 1.5,
                  spreadRadius: 8,
                ),
              ],
            ),
            child: Material(
              color: Colors.transparent,
              shape: const CircleBorder(),
              child: Ink(
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      Color(0xFFFF416C),
                      Color(0xFFFF4B2B),
                      Color(0xFFDC2626),
                    ],
                    stops: [0.2, 0.7, 1.0],
                  ),
                ),
                child: InkWell(
                  customBorder: const CircleBorder(),
                  onTap: widget.isLoading ? null : widget.onPressed,
                  splashColor: Colors.white.withOpacity(0.3),
                  child: Center(
                    child: widget.isLoading
                        ? const CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 3.5,
                          )
                        : Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: const [
                              Icon(
                                Icons.warning_rounded,
                                size: 40,
                                color: Colors.white,
                              ),
                              SizedBox(height: 4),
                              Text(
                                'SOS',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 26,
                                  fontWeight: FontWeight.w900,
                                  letterSpacing: 3.0,
                                ),
                              ),
                              Text(
                                'HOLD / TAP',
                                style: TextStyle(
                                  color: Colors.white70,
                                  fontSize: 9,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 1.5,
                                ),
                              ),
                            ],
                          ),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
