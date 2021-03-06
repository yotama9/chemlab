'''Outline effect'''

from ..textures import Texture
from ..shaders import set_uniform

from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
from OpenGL.arrays import vbo

import numpy as np
import os

class OutlineEffect(object):
    
    def __init__(self, widget, kind='depthnormal'):
        self.widget = widget
        curdir = os.path.dirname(__file__)
        vert = open(os.path.join(curdir, 'shaders', 'noeffect.vert')).read()
        frag = open(os.path.join(curdir, 'shaders', 'outline.frag')).read()        
        # Compile quad shader
        vertex = shaders.compileShader(vert, GL_VERTEX_SHADER)
        fragment = shaders.compileShader(frag, GL_FRAGMENT_SHADER)
        
        if kind not in ['depthnormal', 'depthonly', 'normalonly']:
            raise Exception('The kind of outline should be choosen between depthnormal, depthonly and normalonly')
        
        self.kind = kind
        
        self.quad_program = shaders.compileProgram(vertex, fragment)

    def render(self, fb, texturedict):
        glBindFramebuffer(GL_FRAMEBUFFER, fb)
        glViewport(0, 0, self.widget.width(), self.widget.height())
            
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.quad_program)
        
        set_uniform(self.quad_program, 'whichoutline', '1i',
                    {'depthnormal' : 0, 'depthonly': 1, 'normalonly': 2}[self.kind])
        
        inv_projection = np.linalg.inv(self.widget.camera.projection)
        
        set_uniform(self.quad_program, 'inv_projection', 'mat4fv',
                    inv_projection)
        
        normal_id = glGetUniformLocation(self.quad_program, "s_norm")
        glUniform1i(normal_id, 0)        
        
        depth_id = glGetUniformLocation(self.quad_program, "s_depth")
        glUniform1i(depth_id, 1)

        color_id = glGetUniformLocation(self.quad_program, "s_color")
        glUniform1i(color_id, 2)
        
        # Setting up the texture
        glActiveTexture(GL_TEXTURE0)
        texturedict['normal'].bind()

        glActiveTexture(GL_TEXTURE1)
        texturedict['depth'].bind()
        
        glActiveTexture(GL_TEXTURE2)
        texturedict['color'].bind()
        
        # Set resolution
        res_id = glGetUniformLocation(self.quad_program, "texcoordOffset")
        glUniform2f(res_id, 1.0/self.widget.width(), 1.0/self.widget.height())

        # # Let's render a quad
        quad_data = np.array([-1.0, -1.0, 0.0,
                              1.0, -1.0, 0.0,
                              -1.0,  1.0, 0.0,
                              -1.0,  1.0, 0.0,
                              1.0, -1.0, 0.0,
                              1.0,  1.0, 0.0],
                             dtype='float32')
        
        vboquad = vbo.VBO(quad_data)
        vboquad.bind()
        
        glVertexPointer(3, GL_FLOAT, 0, None)        
        glEnableClientState(GL_VERTEX_ARRAY)

        # draw "count" points from the VBO
        glDrawArrays(GL_TRIANGLES, 0, 6)
        
        vboquad.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        
    def on_resize(self, w, h):
        pass