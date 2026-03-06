import { NextRequest, NextResponse } from 'next/server'

const LOCAL_BACKEND_URL = 'http://localhost:8000'
const RAILWAY_BACKEND_URL = 'https://elyx-production.up.railway.app'

const BACKEND_URL =
    process.env.BACKEND_URL ||
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    (process.env.VERCEL ? RAILWAY_BACKEND_URL : LOCAL_BACKEND_URL)

const NORMALIZED_BACKEND_URL = BACKEND_URL.replace(/\/+$/, '')

async function parseBackendResponse(response: Response): Promise<unknown> {
    const contentType = response.headers.get('content-type') || ''
    if (contentType.includes('application/json')) {
        return response.json()
    }
    const text = await response.text()
    if (!text) return {}
    try {
        return JSON.parse(text)
    } catch {
        return { detail: text }
    }
}

function getTgHeaders(request: NextRequest): Record<string, string> {
    const headers: Record<string, string> = {}
    const initData = request.headers.get('tg-init-data')
    const tgId = request.headers.get('x-telegram-id')
    if (initData) headers['tg-init-data'] = initData
    if (tgId) headers['x-telegram-id'] = tgId
    return headers
}

export async function GET(
    request: NextRequest,
    { params }: { params: { path: string[] } }
) {
    const path = params.path.join('/')
    const searchParams = request.nextUrl.searchParams.toString()
    const url = `${NORMALIZED_BACKEND_URL}/${path}${searchParams ? `?${searchParams}` : ''}`

    try {
        const response = await fetch(url, {
            headers: { 'Content-Type': 'application/json', ...getTgHeaders(request) },
            cache: 'no-store',
        })
        const data = await parseBackendResponse(response)
        return NextResponse.json(data, { status: response.status })
    } catch (error) {
        console.error('API proxy GET error:', error)
        return NextResponse.json({ error: 'Backend unavailable' }, { status: 503 })
    }
}

export async function POST(
    request: NextRequest,
    { params }: { params: { path: string[] } }
) {
    const path = params.path.join('/')
    const url = `${NORMALIZED_BACKEND_URL}/${path}`
    const body = await request.json().catch(() => ({}))

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getTgHeaders(request) },
            body: JSON.stringify(body),
        })
        const data = await parseBackendResponse(response)
        return NextResponse.json(data, { status: response.status })
    } catch (error) {
        console.error('API proxy POST error:', error)
        return NextResponse.json({ error: 'Backend unavailable' }, { status: 503 })
    }
}

export async function PUT(
    request: NextRequest,
    { params }: { params: { path: string[] } }
) {
    const path = params.path.join('/')
    const url = `${NORMALIZED_BACKEND_URL}/${path}`
    const body = await request.json().catch(() => ({}))

    try {
        const response = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', ...getTgHeaders(request) },
            body: JSON.stringify(body),
        })
        const data = await parseBackendResponse(response)
        return NextResponse.json(data, { status: response.status })
    } catch (error) {
        console.error('API proxy PUT error:', error)
        return NextResponse.json({ error: 'Backend unavailable' }, { status: 503 })
    }
}

export async function DELETE(
    request: NextRequest,
    { params }: { params: { path: string[] } }
) {
    const path = params.path.join('/')
    const url = `${NORMALIZED_BACKEND_URL}/${path}`

    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json', ...getTgHeaders(request) },
        })
        const data = await parseBackendResponse(response)
        return NextResponse.json(data, { status: response.status })
    } catch (error) {
        console.error('API proxy DELETE error:', error)
        return NextResponse.json({ error: 'Backend unavailable' }, { status: 503 })
    }
}
