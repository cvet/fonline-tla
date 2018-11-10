Effect Pass 0 BlendEquation GL_MAX

#version 110

const float BordersPower = 5.0;
const float FogBlackout = 0.2;

#ifdef VERTEX_SHADER
uniform mat4 ProjectionMatrix;

attribute vec2 InPosition;
attribute vec4 InColor;

varying vec4 Color;

void main( void )
{
	gl_Position = ProjectionMatrix * vec4( InPosition, 0.0, 1.0 );
	Color = InColor;
}
#endif

#ifdef FRAGMENT_SHADER
varying vec4 Color;

void main( void )
{
	// Input:
	// a - fog area or attack area (0.0 or 1.0)
	// r - actual distance
	// g - whole distance
	
	// Place fog area in r channel
	if( Color.a == 0.0 )
	{
		float value = ( 1.0 - Color.r ) * BordersPower;
		gl_FragColor = vec4( max( value, FogBlackout ), 0.0, 0.0, 0.0 );
	}
	// Place attack area in g/b channel
	else
	{
		float value = ( 1.0 - Color.r ) * BordersPower;
		gl_FragColor = vec4( 0.0, value, Color.g, 0.0 );
	}
}
#endif
