"""
RAG Commands

CLI commands for Advanced RAG & Retrieval features (v1.6.0).
"""

import click
import json
from pathlib import Path
from typing import Optional

from ...modules.context_manager import (
    CodeBERTEmbedder,
    CodeBERTIndex,
    MultiModalRetriever,
    QueryEnhancer,
    GraphRetriever
)


@click.group()
def rag():
    """Advanced RAG & Retrieval commands (v1.6.0)"""
    pass


@rag.command()
@click.argument('file_path')
@click.option('--language', '-l', default='python', help='Programming language')
@click.option('--output', '-o', help='Output file for embeddings')
@click.pass_context
def embed(ctx, file_path: str, language: str, output: Optional[str]):
    """Generate CodeBERT embeddings for a file"""
    try:
        click.echo(f"Generating CodeBERT embeddings for: {file_path}")
        
        embedder = CodeBERTEmbedder()
        embeddings = embedder.embed_file(file_path)
        
        click.echo(f"✓ Generated {len(embeddings)} embeddings")
        
        if output:
            # Save embeddings
            import numpy as np
            data = {
                'file': file_path,
                'language': language,
                'embeddings': [(chunk, emb.tolist()) for chunk, emb in embeddings]
            }
            with open(output, 'w') as f:
                json.dump(data, f)
            click.echo(f"✓ Saved embeddings to: {output}")
        
        # Show statistics
        model_info = embedder.get_model_info()
        click.echo(f"\nModel: {model_info['model_name']}")
        click.echo(f"Device: {model_info['device']}")
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@rag.command()
@click.argument('directory')
@click.option('--index-dir', '-i', default='.uaide/codebert_index', help='Index directory')
@click.option('--chunk-size', '-c', default=100, help='Lines per chunk')
@click.pass_context
def index_codebert(ctx, directory: str, index_dir: str, chunk_size: int):
    """Index a directory with CodeBERT"""
    try:
        click.echo(f"Indexing directory with CodeBERT: {directory}")
        
        index = CodeBERTIndex(index_dir)
        
        # Index all Python files
        from pathlib import Path
        files_indexed = 0
        for file_path in Path(directory).rglob('*.py'):
            if index.index_file(str(file_path), chunk_size):
                files_indexed += 1
                click.echo(f"  ✓ Indexed: {file_path}")
        
        # Save index
        index.save()
        
        click.echo(f"\n✓ Indexed {files_indexed} files")
        click.echo(f"✓ Index saved to: {index_dir}")
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@rag.command()
@click.argument('query')
@click.option('--index-dir', '-i', default='.uaide/codebert_index', help='Index directory')
@click.option('--top-k', '-k', default=5, help='Number of results')
@click.option('--language', '-l', default='python', help='Programming language')
@click.pass_context
def search_codebert(ctx, query: str, index_dir: str, top_k: int, language: str):
    """Search indexed code with CodeBERT"""
    try:
        click.echo(f"Searching for: {query}")
        
        index = CodeBERTIndex(index_dir)
        if not index.load():
            click.echo("✗ No index found. Run 'uaide rag index-codebert' first.", err=True)
            raise click.Abort()
        
        results = index.search(query, language, top_k)
        
        if not results:
            click.echo("No results found.")
            return
        
        click.echo(f"\nFound {len(results)} results:\n")
        for i, (file_path, chunk, similarity) in enumerate(results, 1):
            click.echo(f"{i}. {file_path} (similarity: {similarity:.3f})")
            click.echo(f"   {chunk[:100]}...")
            click.echo()
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@rag.command()
@click.argument('directory')
@click.option('--code-ext', '-c', multiple=True, default=['.py', '.js', '.ts'], help='Code extensions')
@click.option('--doc-ext', '-d', multiple=True, default=['.md', '.txt'], help='Doc extensions')
@click.pass_context
def index_multimodal(ctx, directory: str, code_ext: tuple, doc_ext: tuple):
    """Index directory with multi-modal retrieval"""
    try:
        click.echo(f"Indexing directory (multi-modal): {directory}")
        
        retriever = MultiModalRetriever()
        stats = retriever.index_directory(directory, list(code_ext), list(doc_ext))
        
        click.echo(f"\n✓ Indexed {stats['code_files']} code files")
        click.echo(f"✓ Indexed {stats['doc_files']} documentation files")
        if stats['errors'] > 0:
            click.echo(f"⚠ {stats['errors']} errors occurred")
        
        # Show statistics
        retriever_stats = retriever.get_statistics()
        click.echo(f"\nTotal chunks: {retriever_stats['total_chunks']}")
        click.echo(f"  Code: {retriever_stats['code_chunks']}")
        click.echo(f"  Docs: {retriever_stats['doc_chunks']}")
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@rag.command()
@click.argument('query')
@click.option('--mode', '-m', type=click.Choice(['both', 'code', 'docs']), default='both', help='Search mode')
@click.option('--top-k', '-k', default=10, help='Number of results')
@click.pass_context
def search_multimodal(ctx, query: str, mode: str, top_k: int):
    """Search with multi-modal retrieval"""
    try:
        click.echo(f"Searching ({mode}): {query}")
        
        retriever = MultiModalRetriever()
        # Note: In production, you'd load a saved index
        results = retriever.cross_modal_search(query, mode, top_k)
        
        if not results:
            click.echo("No results found.")
            return
        
        click.echo(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            click.echo(f"{i}. [{result.source_type}] {result.file_path}")
            click.echo(f"   Similarity: {result.similarity:.3f}")
            click.echo(f"   {result.content[:100]}...")
            click.echo()
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@rag.command()
@click.argument('query')
@click.option('--synonyms/--no-synonyms', default=True, help='Add synonyms')
@click.option('--expansion/--no-expansion', default=True, help='Expand query')
@click.option('--llm/--no-llm', default=False, help='Use LLM reformulation')
@click.pass_context
def enhance_query(ctx, query: str, synonyms: bool, expansion: bool, llm: bool):
    """Enhance a search query"""
    try:
        click.echo(f"Enhancing query: {query}")
        
        # Get AI backend if LLM is requested
        ai_backend = None
        if llm:
            from ...ai.backend import AIBackend
            config = ctx.obj['config']
            ai_backend = AIBackend(config)
        
        enhancer = QueryEnhancer(ai_backend)
        result = enhancer.enhance_query(query, synonyms, expansion, llm)
        
        click.echo(f"\nOriginal: {result['original']}")
        click.echo(f"Enhanced: {result['enhanced']}")
        
        if result['expansions']:
            click.echo(f"\nExpansions ({len(result['expansions'])}):")
            for exp in result['expansions']:
                click.echo(f"  • {exp}")
        
        if result['reformulations']:
            click.echo(f"\nReformulations ({len(result['reformulations'])}):")
            for ref in result['reformulations']:
                click.echo(f"  • {ref}")
        
        # Detect intent
        intent = enhancer.detect_intent(query)
        click.echo(f"\nDetected intent: {intent}")
        
        # Suggest filters
        filters = enhancer.suggest_filters(query)
        if any(filters.values()):
            click.echo("\nSuggested filters:")
            for filter_type, values in filters.items():
                if values:
                    click.echo(f"  {filter_type}: {', '.join(values)}")
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@rag.command()
@click.argument('directory')
@click.option('--extensions', '-e', multiple=True, default=['.py'], help='File extensions')
@click.pass_context
def build_graph(ctx, directory: str, extensions: tuple):
    """Build call graph from code"""
    try:
        click.echo(f"Building call graph for: {directory}")
        
        retriever = GraphRetriever()
        stats = retriever.index_directory(directory, list(extensions))
        
        click.echo(f"\n✓ Indexed {stats['files']} files")
        click.echo(f"✓ Found {stats['nodes']} code nodes")
        if stats['errors'] > 0:
            click.echo(f"⚠ {stats['errors']} errors occurred")
        
        # Show statistics
        graph_stats = retriever.get_statistics()
        click.echo(f"\nGraph statistics:")
        click.echo(f"  Total nodes: {graph_stats['total_nodes']}")
        click.echo(f"  Total files: {graph_stats['total_files']}")
        click.echo(f"  Dependencies: {graph_stats['total_dependencies']}")
        click.echo(f"  Avg dependencies per node: {graph_stats['avg_dependencies']:.2f}")
        click.echo(f"\nNode types:")
        for node_type, count in graph_stats['node_types'].items():
            click.echo(f"  {node_type}: {count}")
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@rag.command()
@click.argument('name')
@click.option('--depth', '-d', default=2, help='Expansion depth')
@click.pass_context
def expand_context(ctx, name: str, depth: int):
    """Expand context around a code node"""
    try:
        click.echo(f"Expanding context for: {name}")
        
        retriever = GraphRetriever()
        # Note: In production, you'd load a saved graph
        
        context = retriever.expand_context(name, depth)
        
        if not context:
            click.echo(f"✗ Node not found: {name}", err=True)
            raise click.Abort()
        
        click.echo("\nExpanded context:\n")
        click.echo(context)
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@rag.command()
@click.argument('name')
@click.option('--max-results', '-m', default=10, help='Maximum results')
@click.pass_context
def find_related(ctx, name: str, max_results: int):
    """Find code related to a node"""
    try:
        click.echo(f"Finding code related to: {name}")
        
        retriever = GraphRetriever()
        related = retriever.find_related_code(name, max_results)
        
        if not related:
            click.echo("No related code found.")
            return
        
        click.echo(f"\nFound {len(related)} related nodes:\n")
        for i, node in enumerate(related, 1):
            click.echo(f"{i}. {node.name} ({node.node_type})")
            click.echo(f"   File: {node.file_path}:{node.line_number}")
            click.echo(f"   Dependencies: {len(node.dependencies)}")
            click.echo()
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@rag.command()
@click.argument('from_name')
@click.argument('to_name')
@click.pass_context
def call_chain(ctx, from_name: str, to_name: str):
    """Find call chain between two nodes"""
    try:
        click.echo(f"Finding call chain: {from_name} → {to_name}")
        
        retriever = GraphRetriever()
        chain = retriever.get_call_chain(from_name, to_name)
        
        if not chain:
            click.echo("No call chain found.")
            return
        
        click.echo(f"\nCall chain ({len(chain)} steps):\n")
        for i, node_name in enumerate(chain):
            if i > 0:
                click.echo("  ↓")
            click.echo(f"{i + 1}. {node_name}")
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@rag.command()
@click.pass_context
def stats(ctx):
    """Show RAG system statistics"""
    try:
        click.echo("RAG System Statistics\n")
        
        # CodeBERT
        embedder = CodeBERTEmbedder()
        model_info = embedder.get_model_info()
        click.echo("CodeBERT Embedder:")
        click.echo(f"  Model: {model_info['model_name']}")
        click.echo(f"  Device: {model_info['device']}")
        click.echo(f"  Loaded: {model_info['loaded']}")
        click.echo(f"  Supported languages: {len(model_info['supported_languages'])}")
        
        # Query Enhancer
        enhancer = QueryEnhancer()
        enhancer_stats = enhancer.get_statistics()
        click.echo("\nQuery Enhancer:")
        click.echo(f"  Synonym groups: {enhancer_stats['synonym_groups']}")
        click.echo(f"  Total synonyms: {enhancer_stats['total_synonyms']}")
        click.echo(f"  Pattern groups: {enhancer_stats['pattern_groups']}")
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()
