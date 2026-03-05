import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

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
    const url = `${BACKEND_URL}/${path}${searchParams ? `?${searchParams}` : ''}`

    try {
        const response = await fetch(url, {
            headers: { 'Content-Type': 'application/json', ...getTgHeaders(request) },
            cache: 'no-store',
        })
        const data = await response.json()
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
    const url = `${BACKEND_URL}/${path}`
    const body = await request.json().catch(() => ({}))

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getTgHeaders(request) },
            body: JSON.stringify(body),
        })
        const data = await response.json()
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
    const url = `${BACKEND_URL}/${path}`
    const body = await request.json().catch(() => ({}))

    try {
        const response = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', ...getTgHeaders(request) },
            body: JSON.stringify(body),
        })
        const data = await response.json()
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
    const url = `${BACKEND_URL}/${path}`

    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json', ...getTgHeaders(request) },
        })
        const data = await response.json().catch(() => ({}))
        return NextResponse.json(data, { status: response.status })
    } catch (error) {
        console.error('API proxy DELETE error:', error)
        return NextResponse.json({ error: 'Backend unavailable' }, { status: 503 })
    }
}
