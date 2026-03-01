# Cómo usar esta wiki

Esta carpeta es la fuente de verdad de la documentación wiki del proyecto.

## Estructura

- Entrada principal: [Home.md](Home.md)
- Páginas temáticas: arquitectura, instalación, datos, operación y FAQ.

## Publicación en GitHub Wiki

Usa el script de sincronización:

```bash
bash scripts/publish_wiki.sh Idromerom714 Tutor-Icfes-AI
```

El script:

1. Clona (o reutiliza) `.wiki/`.
2. Sincroniza `docs/wiki/` hacia `.wiki/` con `rsync --delete`.
3. Crea commit automático si hay cambios.
4. Publica con `git push` al repo wiki.

## Nota

Para publicar, debes tener permisos de push al repositorio y autenticación GitHub configurada en el entorno.
