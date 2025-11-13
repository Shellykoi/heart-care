import React, { useMemo } from 'react';

type AppointmentStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'rejected' | string;

interface AppointmentRecord {
  id?: number | string;
  appointment_date?: string | Date;
  status?: AppointmentStatus;
}

interface ConsultationCalendarProps {
  appointments?: AppointmentRecord[];
  loading?: boolean;
  title?: string;
}

const WEEKDAY_LABELS = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];

const containerStyle: React.CSSProperties = {
  backgroundColor: '#000000',
  color: '#EAEAEA',
  borderRadius: '24px',
  padding: '24px',
  boxShadow: '0 20px 40px rgba(0,0,0,0.4)',
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  width: '100%',
  minWidth: 0,
  flex: '1 1 auto',
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'flex-start',
  justifyContent: 'space-between',
  paddingBottom: '24px',
};

const titleGroupStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
};

const titleStyle: React.CSSProperties = {
  fontSize: '24px',
  fontWeight: 600,
  color: '#FFFFFF',
  margin: 0,
};

const subtitleStyle: React.CSSProperties = {
  fontSize: '14px',
  color: '#8E8E93',
  margin: 0,
};

const monthGroupStyle: React.CSSProperties = {
  textAlign: 'right',
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
};

const monthNameStyle: React.CSSProperties = {
  fontSize: '14px',
  fontWeight: 500,
  color: '#8E8E93',
  margin: 0,
};

const monthYearStyle: React.CSSProperties = {
  fontSize: '12px',
  color: '#5E5E60',
  margin: 0,
};

const calendarBodyStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '16px',
};

const gridWrapperStyle: React.CSSProperties = {
  width: '100%',
  display: 'flex',
  flexDirection: 'column',
  rowGap: '12px',
};

const weekdayGridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(7, minmax(0, 1fr))',
  columnGap: '6px',
  rowGap: '6px',
  textAlign: 'center',
};

const weekdayLabelStyle: React.CSSProperties = {
  fontSize: '12px',
  fontWeight: 500,
  color: '#8E8E93',
};

const daysGridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(7, minmax(0, 1fr))',
  columnGap: '6px',
  rowGap: '12px',
  justifyItems: 'center',
};

const dayCellBaseStyle: React.CSSProperties = {
  width: '100%',
  maxWidth: '56px',
  minWidth: '44px',
  aspectRatio: '1 / 1',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  borderRadius: '9999px',
  fontSize: '14px',
  fontWeight: 500,
  position: 'relative',
  userSelect: 'none',
  color: '#8E8E93',
  border: '1px solid transparent',
  transition: 'transform 0.2s ease',
};

const dayStatusStyles: Record<string, React.CSSProperties> = {
  done: {
    backgroundColor: '#FFD60A',
    color: '#1C1C1E',
    fontWeight: 600,
  },
  scheduled: {
    backgroundColor: 'rgba(120, 120, 128, 0.36)',
    color: '#FFFFFF',
  },
};

const todayStyle: React.CSSProperties = {
  borderColor: '#5E5E60',
};

const skeletonCellStyle: React.CSSProperties = {
  ...dayCellBaseStyle,
  backgroundColor: 'rgba(46, 46, 48, 0.6)',
};

const legendContainerStyle: React.CSSProperties = {
  marginTop: 'auto',
  paddingTop: '24px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: '24px',
  fontSize: '12px',
  color: '#8E8E93',
};

const legendItemStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
};

const legendDotBaseStyle: React.CSSProperties = {
  width: '12px',
  height: '12px',
  borderRadius: '9999px',
};

const normalizeDateKey = (date: Date) => {
  return `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
};

const normalizeStatus = (status: AppointmentStatus | undefined): AppointmentStatus => {
  if (!status) return 'pending';
  if (typeof status === 'string') {
    return status.toLowerCase().replace(/^appointmentstatus\./, '');
  }
  if (typeof status === 'object' && 'value' in (status as Record<string, unknown>)) {
    return normalizeStatus((status as { value?: AppointmentStatus }).value);
  }
  if (typeof status === 'object' && 'name' in (status as Record<string, unknown>)) {
    return normalizeStatus((status as { name?: AppointmentStatus }).name);
  }
  return 'pending';
};

const classifyDayStatus = (dayAppointments: AppointmentRecord[]) => {
  if (dayAppointments.length === 0) return 'idle';

  const statuses = dayAppointments.map((appointment) => normalizeStatus(appointment.status));

  if (statuses.some((status) => status === 'confirmed' || status === 'completed')) {
    return 'done';
  }

  if (statuses.some((status) => status === 'pending')) {
    return 'scheduled';
  }

  return 'idle';
};

export function ConsultationCalendar({
  appointments = [],
  loading = false,
  title = '我的咨询日程',
}: ConsultationCalendarProps) {
  const today = useMemo(() => new Date(), []);
  const calendarYear = today.getFullYear();
  const calendarMonth = today.getMonth();

  const groupedAppointments = useMemo(() => {
    const grouped = new Map<string, AppointmentRecord[]>();

    appointments.forEach((appointment) => {
      const value = appointment?.appointment_date;
      if (!value) return;

      const dateObj = value instanceof Date ? value : new Date(value);
      if (Number.isNaN(dateObj.getTime())) return;

      const normalized = new Date(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate());
      const key = normalizeDateKey(normalized);

      if (!grouped.has(key)) {
        grouped.set(key, []);
      }
      grouped.get(key)!.push(appointment);
    });

    return grouped;
  }, [appointments]);

  const firstDayOfMonth = useMemo(
    () => new Date(calendarYear, calendarMonth, 1),
    [calendarYear, calendarMonth]
  );

  const daysInMonth = useMemo(
    () => new Date(calendarYear, calendarMonth + 1, 0).getDate(),
    [calendarYear, calendarMonth]
  );

  const leadingEmptyCells = useMemo(() => {
    const day = firstDayOfMonth.getDay();
    return (day + 6) % 7;
  }, [firstDayOfMonth]);

  const monthName = useMemo(
    () => firstDayOfMonth.toLocaleString('en-US', { month: 'long' }),
    [firstDayOfMonth]
  );

  const skeletonDays = Array.from({ length: 35 }, (_, index) => (
    <div
      // eslint-disable-next-line react/no-array-index-key
      key={`skeleton-${index}`}
      style={skeletonCellStyle}
      className="animate-pulse"
    />
  ));

  const renderDays = () => {
    const cells: React.ReactNode[] = [];

    for (let i = 0; i < leadingEmptyCells; i += 1) {
      cells.push(
        <div
          key={`empty-${i}`}
          style={dayCellBaseStyle}
          aria-hidden
        />
      );
    }

    for (let day = 1; day <= daysInMonth; day += 1) {
      const date = new Date(calendarYear, calendarMonth, day);
      const key = normalizeDateKey(date);
      const dayAppointments = groupedAppointments.get(key) ?? [];
      const status = classifyDayStatus(dayAppointments);

      const isToday =
        date.getFullYear() === today.getFullYear() &&
        date.getMonth() === today.getMonth() &&
        date.getDate() === today.getDate();

      const dayStyle: React.CSSProperties = {
        ...dayCellBaseStyle,
        ...(dayStatusStyles[status] ?? {}),
        ...(isToday ? todayStyle : {}),
      };

      cells.push(
        <div
          key={day}
          style={dayStyle}
          aria-label={`${
            calendarMonth + 1
          }月${day}日${status !== 'idle' ? '有咨询安排' : '暂无咨询安排'}`}
        >
          {day}
          {status === 'done' && (
            <span
              style={{
                position: 'absolute',
                bottom: '-2px',
                right: '6px',
                height: '8px',
                width: '8px',
                borderRadius: '9999px',
                backgroundColor: 'rgba(255, 214, 10, 0.8)',
                boxShadow: '0 0 8px rgba(255, 214, 10, 0.6)',
              }}
            />
          )}
        </div>
      );
    }

    return cells;
  };

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <div style={titleGroupStyle}>
          <h3 style={titleStyle}>{title}</h3>
          <p style={subtitleStyle}>一目了然查看本月咨询安排</p>
        </div>
        <div style={monthGroupStyle}>
          <p style={monthNameStyle}>{monthName}</p>
          <p style={monthYearStyle}>{calendarYear}</p>
        </div>
      </div>

      <div style={calendarBodyStyle}>
        <div style={gridWrapperStyle}>
          <div style={weekdayGridStyle}>
            {WEEKDAY_LABELS.map((label, index) => (
              <div key={`${label}-${index}`} style={weekdayLabelStyle}>
                {label}
              </div>
            ))}
          </div>

          <div style={daysGridStyle}>
            {loading ? skeletonDays : renderDays()}
          </div>
        </div>
      </div>

      <div style={legendContainerStyle}>
        <div style={legendItemStyle}>
          <span
            style={{
              ...legendDotBaseStyle,
              border: '1px solid #8E8E93',
              backgroundColor: 'transparent',
            }}
          />
          <span>今天</span>
        </div>
        <div style={legendItemStyle}>
          <span
            style={{
              ...legendDotBaseStyle,
              backgroundColor: '#FFD60A',
            }}
          />
          <span>已确认/完成</span>
        </div>
        <div style={legendItemStyle}>
          <span
            style={{
              ...legendDotBaseStyle,
              backgroundColor: 'rgba(120, 120, 128, 0.36)',
            }}
          />
          <span>待安排</span>
        </div>
      </div>
    </div>
  );
}

