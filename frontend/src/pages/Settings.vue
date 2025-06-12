<template>
  <div class="min-h-screen bg-gray-100">
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="flex items-center space-x-4 mb-8">
          <svg width="48" height="48" viewBox="0 0 128 128" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="brainGradient" x1="64" y1="40" x2="64" y2="88" gradientUnits="userSpaceOnUse">
                <stop stop-color="#38BDF8"/>
                <stop offset="1" stop-color="#34D399"/>
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            <path d="M99.5 60C108 60 112 69.5 110.5 76.5C114.5 79.5 113.5 88.5 107 91.5C100.5 102 86.5 100 80.5 96.5C77.5 104.5 65.5 105 60.5 99C53.5 101.5 45.5 98.5 43 91.5C36 94 28 89.5 28.5 82C23 80 20.5 71.5 25 66.5C21.5 60 27.5 53 34.5 53C37.5 44.5 49 41.5 56.5 47.5C62.5 40.5 74.5 42 79.5 48.5C87.5 44 94 49 99.5 60Z" fill="transparent" stroke="#4B5563" stroke-width="2"/>
            <g filter="url(#glow)">
              <path d="M64 54C61.2386 54 59 56.2386 59 59V64H54C51.2386 64 49 66.2386 49 69C49 71.7614 51.2386 74 54 74H59V79C59 81.7614 61.2386 84 64 84C66.7614 84 69 81.7614 69 79V74H74C76.7614 74 79 71.7614 79 69C79 66.2386 76.7614 64 74 64H69V59C69 56.2386 66.7614 54 64 54Z" fill="url(#brainGradient)"/>
              <path d="M64 40V49M64 89V98M88 64H97M40 64H49M80 48L85 43M48 80L43 85M80 80L85 85M48 48L43 43" stroke="url(#brainGradient)" stroke-width="3" stroke-linecap="round"/>
            </g>
          </svg>
          <h1 class="text-3xl font-bold text-gray-900">存储设置</h1>
        </div>
      </div>
    </div>
  </div>
</template> 