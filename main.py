import pygame
import zengl
import sys
import asyncio


SCREEN_SIZE = (1600, 900)
GRID_SIZE = (100, 100)

flags = pygame.OPENGL | pygame.DOUBLEBUF

pygame.display.set_mode(SCREEN_SIZE, flags)

ctx = zengl.context()

image = ctx.image(SCREEN_SIZE, 'rgba8unorm')
output = ctx.image(SCREEN_SIZE, 'rgba8unorm')

pipeline = ctx.pipeline(
    vertex_shader="""
        #version 300 es
        precision highp float;

        vec2 vertex[4] = vec2[](
            vec2(-1.0, -1.0),
            vec2(-1.0, 1.0),
            vec2(1.0, -1.0),
            vec2(1.0, 1.0)
        );

        out vec2 uv;

        void main() {
            uv = vertex[gl_VertexID] * vec2(0.5, -0.5) + 0.5;
            gl_Position = vec4(vertex[gl_VertexID], 0.0, 1.0);
        }
    """,
    fragment_shader="""
        #version 300 es
        precision highp float;

        uniform sampler2D Texture;

        in vec2 uv;
        out vec4 out_color;

        void main() {
            out_color = texture(Texture, uv).bgra;
        }
    """,
    layout=[
        {
            "name": "Texture",
            "binding": 0,
        },
    ],
    resources=[
        {
            "type": "sampler",
            "binding": 0,
            "image": image,
            "min_filter": "nearest",
            "mag_filter": "nearest",
        },
    ],
    framebuffer=None,
    viewport=(0, 0, *SCREEN_SIZE),
    topology='triangle_strip',
    vertex_count=4,
)

clock = pygame.time.Clock()

pygame.font.init()
font = pygame.font.Font('assets/RobotoMono-Bold.ttf', SCREEN_SIZE[1]//12)
display_surf = pygame.surface.Surface(SCREEN_SIZE)


def draw_grid(surface: pygame.Surface):
    grid = [
        x for x in range(0, SCREEN_SIZE[0], GRID_SIZE[0]) 
        for y in range(0, SCREEN_SIZE[1], GRID_SIZE[1])
    ]
    for i in grid:
        pygame.draw.line(surface, (200, 200, 200), (i, 0), (i, SCREEN_SIZE[1]))
        pygame.draw.line(surface, (200, 200, 200), (0, i), (SCREEN_SIZE[0], i))      


def draw_text(
        mouse_pos: tuple[int], 
        screen_size: tuple[int], 
        grid_size: tuple[int], 
        surface: pygame.Surface
    ):

    mouse_coords_surf = font.render(f"mouse_coords:{mouse_pos}", True, (225, 0, 0))
    mouse_coords_rect = mouse_coords_surf.get_rect()
    mouse_coords_surf_pos = (
        screen_size[0] // 2 - mouse_coords_rect.w // 2, 
        screen_size[1] // 3
    )

    screen_size_surf = font.render(f"screen_size:{screen_size}", True, (0, 255, 0))
    screen_size_rect = screen_size_surf.get_rect()
    screen_size_surf_pos = (
        screen_size[0] // 2 - screen_size_rect.w // 2, 
        mouse_coords_surf_pos[1] + mouse_coords_rect.h*2
    )

    grid_size_surf = font.render(f"grid_size:{grid_size}", True, (0, 255, 255))
    grid_size_rect = grid_size_surf.get_rect()
    grid_size_surf_pos = (
        screen_size[0] // 2 - grid_size_rect.w // 2, 
        screen_size_surf_pos[1] + screen_size_rect.h*2
    )

    surface.blit(mouse_coords_surf, mouse_coords_surf_pos)
    surface.blit(screen_size_surf, screen_size_surf_pos)
    surface.blit(grid_size_surf, grid_size_surf_pos)


async def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        mouse_coords = pygame.mouse.get_pos()  

        display_surf.fill((0, 0, 0))
        draw_grid(display_surf)      
        draw_text(mouse_coords, SCREEN_SIZE, GRID_SIZE, display_surf)
        image.write(pygame.image.tobytes(display_surf, "RGBA", True))

        ctx.new_frame()
        pipeline.render()
        image.blit(output)
        output.blit()
        ctx.end_frame()

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
